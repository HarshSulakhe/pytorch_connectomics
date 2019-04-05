from __future__ import print_function, division

import torch
import torch.nn as nn
import torch.nn.functional as F

class DiceLoss(nn.Module):

    def __init__(self, size_average=True, reduce=True, smooth=100.0):
        super(DiceLoss, self).__init__(size_average, reduce)
        self.smooth = smooth
        self.reduce = reduce

    def dice_loss(self, input, target):
        loss = 0.

        for index in range(input.size()[0]):
            iflat = input[index].view(-1)
            tflat = target[index].view(-1)
            intersection = (iflat * tflat).sum()

            loss += 1 - ((2. * intersection + self.smooth) / 
                    ( (iflat**2).sum() + (tflat**2).sum() + self.smooth))

        # size_average=True for the dice loss
        return loss / float(input.size()[0])

    def dice_loss_batch(self, input, target):

        iflat = input.view(-1)
        tflat = target.view(-1)
        intersection = (iflat * tflat).sum()

        loss = 1 - ((2. * intersection + self.smooth) / 
               ( (iflat**2).sum() + (tflat**2).sum() + self.smooth))
        return loss

    def forward(self, input, target):
        #_assert_no_grad(target)
        if not (target.size() == input.size()):
            raise ValueError("Target size ({}) must be the same as input size ({})".format(target.size(), input.size()))

        if self.reduce:
            loss = self.dice_loss(input, target)
        else:    
            loss = self.dice_loss_batch(input, target)
        return loss

class WeightedMSE(nn.Module):

    def __init__(self):
        super().__init__()

    def weighted_mse_loss(self, input, target, weight):
        s1 = torch.prod(torch.tensor(input.size()[2:]).float())
        s2 = input.size()[0]
        norm_term = (s1 * s2).cuda()
        return torch.sum(weight * (input - target) ** 2) / norm_term

    def forward(self, input, target, weight):
        #_assert_no_grad(target)
        return self.weighted_mse_loss(input, target, weight)  

# define a customized loss function for future development
class WeightedBCE(nn.Module):

    def __init__(self, size_average=True, reduce=True):
        super().__init__()
        self.size_average = size_average
        self.reduce = reduce

    def forward(self, input, target, weight):
        #_assert_no_grad(target)
        return F.binary_cross_entropy(input, target, weight, self.size_average,
                                      self.reduce)