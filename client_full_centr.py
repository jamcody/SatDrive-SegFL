import copy
import torch
import numpy as np
from torch import optim, nn
from collections import defaultdict
from torch.utils.data import DataLoader
from utils.utils import HardNegativeMining, MeanReduction
import torchvision.transforms as T
# TO be deleted
class_eval = [255, 2, 4, 255, 11, 5, 0, 0, 1, 8, 13, 3, 7, 6, 255, 255, 15, 14, 12, 9, 10]

def get_mapping():
        classes = class_eval
        mapping = np.zeros((256,), dtype=np.int64) + 255
        for i, cl in enumerate(classes):
            mapping[i] = cl
        return lambda x: torch.from_numpy(mapping[x])

class ClientCentr:

    def __init__(self, args, dataset_train, dataset_test, model, test_client=False):
        self.args = args
        self.dataset = dataset_train
        self.name = self.dataset.client_name
        self.model = model
        self.device = "cuda"
        self.train_loader = DataLoader(self.dataset, batch_size=self.args.bs, shuffle=True, drop_last=True)
        self.test_loader = DataLoader(dataset_test, batch_size=1, shuffle=False)
        self.criterion = nn.CrossEntropyLoss(ignore_index=255, reduction='none')
        self.reduction = HardNegativeMining() if self.args.hnm else MeanReduction()

    def __str__(self):
        return self.name

    @staticmethod
    def update_metric(metric, outputs, labels):
        _, prediction = outputs.max(dim=1)
        labels = labels.cpu().numpy()
        prediction = prediction.cpu().numpy()
        metric.update(labels, prediction)
    # ADDED
    @staticmethod
    def print_step_loss(losses, step):
        for name, l in losses.items():
            print(f"Train_{name}: {l} at step:{step}")

    def _get_outputs(self, images):
        if self.args.model == 'deeplabv3_mobilenetv2':
            return self.model(images)['out']
        if self.args.model == 'resnet18':
            return self.model(images)
        raise NotImplementedError

    def run_epoch(self, cur_epoch, optimizer):
        """
        This method locally trains the model with the dataset of the client. It handles the training at mini-batch level
        :param cur_epoch: current epoch of training
        :param optimizer: optimizer used for the local training
        """

        # ADDED 
        dict_all_epoch_losses = defaultdict(lambda: 0)
        #self.loader.sampler.set_epoch(cur_epoch)

        for cur_step, (images, labels) in enumerate(self.train_loader):
            images = images.to(self.device, dtype=torch.float32)
            labels = labels.to(self.device, dtype=torch.long)
            optimizer.zero_grad()

            outputs = self._get_outputs(images)
            loss = self.reduction(self.criterion(outputs,labels),labels)
            #loss.backward()
            dict_calc_losses = {'loss_tot': loss}
            dict_calc_losses['loss_tot'].backward()

            """test_print_interval = 100
            if (cur_step + 1) % test_print_interval == 0:
                self.print_step_loss(dict_calc_losses, len(self.train_loader) * cur_epoch + cur_step + 1)"""
            # Backward pass
            # loss.backward()
            # Update parameters
            optimizer.step()

            #optimizer.zero_grad()

            # To update metrics:
            # self.update_metric(metric, outputs, labels)

        print(f"Epoch {cur_epoch} ended.")
        self.print_step_loss(dict_calc_losses, len(self.train_loader) * cur_epoch + cur_step + 1)



    def train(self):
        """
        This method locally trains the model with the dataset of the client. It handles the training at epochs level
        (by calling the run_epoch method for each local epoch of training)
        :return: length of the local dataset, copy of the model parameters
        """
        optimizer = torch.optim.SGD(self.model.parameters(), lr=self.args.lr, weight_decay=self.args.wd, momentum=self.args.m)

        self.model.train()
        for epoch in range(self.args.num_epochs):
            self.run_epoch(epoch, optimizer)

    def test(self, metric):
        """
        This method tests the model on the local dataset of the client.
        :param metric: StreamMetric object
        """
        self.model.eval()
        with torch.no_grad():
            for i, (images, labels) in enumerate(self.test_loader):
                images = images.to(self.device)
                labels = labels.to(self.device)
                # Forward pass
                outputs = self._get_outputs(images) # Apply the loss
                loss = self.reduction(self.criterion(outputs,labels),labels)
                _, prediction = outputs.max(dim=1)
                labels = labels.cpu().numpy()
                prediction = prediction.cpu().numpy()
                metric.update(labels, prediction)

            

        