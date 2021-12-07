import copy
import numpy as np
import torch
import torch.nn as nn

from typing import List
from collections import OrderedDict

NEW_NODES_CHOICE = [16, 32, 64]
MIN_NODES = 16
MAX_NODES = 256

MIN_HIDDEN_LAYERS = 1
MAX_HIDDEN_LAYERS = 5

class EvolvableNN(nn.Module):
    def __init__(self, num_inputs: int, num_outputs: int, hidden_size: List[int], hidden_activation: List[str], 
                output_activation=None, stored_values=None):
        super(EvolvableNN, self).__init__()

        self.num_inputs = num_inputs

        self.hidden_size = hidden_size
        self.hidden_activation = hidden_activation

        self.num_outputs = num_outputs
        self.output_activation = output_activation

        self.net = self.create_net()

        if stored_values is not None:
            self.inject_parameters(pvec=stored_values, without_layer_norm=False)

    def get_activation(self, activation_names):
        activation_functions = {'tanh': nn.Tanh, 'linear': nn.Identity, 'relu': nn.ReLU, 'elu': nn.ELU,
                                'softsign': nn.Softsign, 'sigmoid': nn.Sigmoid, 'softplus': nn.Softplus,
                                'lrelu': nn.LeakyReLU, 'prelu': nn.PReLU, }

        return activation_functions[activation_names]()

    def create_net(self):
        net_dict = OrderedDict()

        net_dict["linear_layer_0"] = nn.Linear(self.num_inputs, self.hidden_size[0])
        net_dict["activation_0"] = self.get_activation(self.hidden_activation[0])

        if len(self.hidden_size) > 1:
            for l_no in range(1, len(self.hidden_size)):
                net_dict[f"linear_layer_{str(l_no)}"] = nn.Linear(self.hidden_size[l_no - 1], self.hidden_size[l_no])
                net_dict[f"activation_{str(l_no)}"] = self.get_activation(self.hidden_activation[l_no])

        output_layer = nn.Linear(self.hidden_size[-1], self.num_outputs)

        net_dict[f"linear_layer_output"] = output_layer
        if self.output_activation is not None:
            net_dict[f"activation_output"] = self.get_activation(self.output_activation)

        return nn.Sequential(net_dict)

    def forward(self, x):
        for value in self.net:
            x = value(x)
        return x

    def get_model_dict(self):

        model_dict = self.init_dict
        model_dict.update({'stored_values': self.extract_parameters(without_layer_norm=False)})
        return model_dict

    def count_parameters(self, without_layer_norm=False):
        count = 0
        for name, param in self.named_parameters():
            if (not without_layer_norm) or (not 'layer_norm' in name):
                count += param.data.cpu().numpy().flatten().shape[0]
        return count

    # function to return current pytorch gradient in same order as genome's flattened parameter vector
    def extract_grad(self, without_layer_norm=False):
        tot_size = self.count_parameters(without_layer_norm)
        pvec = np.zeros(tot_size, np.float32)
        count = 0
        for name, param in self.named_parameters():
            if (not without_layer_norm) or (not 'layer_norm' in name):
                sz = param.grad.data.cpu().numpy().flatten().shape[0]
                pvec[count:count + sz] = param.grad.data.cpu().numpy().flatten()
                count += sz
        return pvec.copy()

    # function to grab current flattened neural network weights
    def extract_parameters(self, without_layer_norm=False):
        tot_size = self.count_parameters(without_layer_norm)
        pvec = np.zeros(tot_size, np.float32)
        count = 0
        for name, param in self.named_parameters():
            if (not without_layer_norm) or (not 'layer_norm' in name):
                sz = param.data.cpu().detach().numpy().flatten().shape[0]
                pvec[count:count + sz] = param.data.cpu().detach().numpy().flatten()
                count += sz
        return copy.deepcopy(pvec)

    # function to inject a flat vector of ANN parameters into the model's current neural network weights
    def inject_parameters(self, pvec, without_layer_norm=False):
        count = 0

        for name, param in self.named_parameters():
            if (not without_layer_norm) or (not 'layer_norm' in name):
                sz = param.data.cpu().numpy().flatten().shape[0]
                raw = pvec[count:count + sz]
                reshaped = raw.reshape(param.data.cpu().numpy().shape)
                param.data = torch.from_numpy(copy.deepcopy(reshaped)).type(torch.FloatTensor)
                count += sz
        return pvec

    def add_layer(self):

        # add layer to hyper params
        if len(self.hidden_size) < MAX_HIDDEN_LAYERS:  # HARD LIMIT
            self.hidden_size += [self.hidden_size[-1]]
            self.hidden_activation += ['relu']
            # copy old params to new net
            new_net = self.create_net()
            new_net = self.preserve_parameters(old_net=self.net, new_net=new_net)
            self.net = new_net

    def remove_layer(self):
        hidden_lenght = len(self.hidden_size)
        if hidden_lenght > MIN_HIDDEN_LAYERS:  # HARD LIMIT
            new_lenght = hidden_lenght - 1
            self.hidden_size = self.hidden_size[:new_lenght]
            self.hidden_activation = self.hidden_activation[:new_lenght]
            new_net = self.create_net()
            new_net = self.shrink_preserve_parameters(old_net=self.net, new_net=new_net)
            self.net = new_net

    def add_node(self, hidden_layer=None, numb_new_nodes=None):

        if hidden_layer is None:
            hidden_layer = np.random.randint(0, len(self.hidden_size), 1)[0]
        else:
            hidden_layer = min(hidden_layer, len(self.hidden_size) - 1)
        if numb_new_nodes is None:
            numb_new_nodes = np.random.choice(NEW_NODES_CHOICE, 1)[0]

        if (self.hidden_size[hidden_layer] + numb_new_nodes) <= 256:  # HARD LIMIT
            self.hidden_size[hidden_layer] += numb_new_nodes
            new_net = self.create_net()
            new_net = self.preserve_parameters(old_net=self.net, new_net=new_net)

            self.net = new_net

        return {"hidden_layer": hidden_layer, "numb_new_nodes": numb_new_nodes}

    def remove_node(self, hidden_layer=None, numb_new_nodes=None):

        if hidden_layer is None:
            hidden_layer = np.random.randint(0, len(self.hidden_size), 1)[0]
        else:
            hidden_layer = min(hidden_layer, len(self.hidden_size) - 1)
        if numb_new_nodes is None:
            numb_new_nodes = np.random.choice(NEW_NODES_CHOICE, 1)[0]

        if self.hidden_size[hidden_layer] - numb_new_nodes > 16:  # HARD LIMIT
            self.hidden_size[hidden_layer] = self.hidden_size[hidden_layer] - numb_new_nodes
            new_net = self.create_net()
            new_net = self.shrink_preserve_parameters(old_net=self.net, new_net=new_net)

            self.net = new_net

        return {"hidden_layer": hidden_layer, "numb_new_nodes": numb_new_nodes}

    def clone(self):
        clone = EvolvableNN(**copy.deepcopy(self.init_dict))
        clone.load_state_dict(self.state_dict())
        return clone

    def preserve_parameters(self, old_net, new_net):

        old_net_dict = dict(old_net.named_parameters())

        for key, param in new_net.named_parameters():
            if key in old_net_dict.keys():
                if old_net_dict[key].data.size() == param.data.size():
                    param.data = old_net_dict[key].data
                else:
                    if not "norm" in key:
                        old_size = old_net_dict[key].data.size()
                        new_size = param.data.size()
                        if len(param.data.size()) == 1:
                            param.data[:min(old_size[0], new_size[0])] = old_net_dict[key].data[
                                                                         :min(old_size[0], new_size[0])]
                        else:
                            param.data[:min(old_size[0], new_size[0]), :min(old_size[1], new_size[1])] = old_net_dict[
                                                                                                             key].data[
                                                                                                         :min(old_size[
                                                                                                                  0],
                                                                                                              new_size[
                                                                                                                  0]),
                                                                                                         :min(old_size[
                                                                                                                  1],
                                                                                                              new_size[
                                                                                                                  1])]

        return new_net

    def shrink_preserve_parameters(self, old_net, new_net):

        old_net_dict = dict(old_net.named_parameters())

        for key, param in new_net.named_parameters():
            if key in old_net_dict.keys():
                if old_net_dict[key].data.size() == param.data.size():
                    param.data = old_net_dict[key].data
                else:
                    if not "norm" in key:
                        old_size = old_net_dict[key].data.size()
                        new_size = param.data.size()
                        min_0 = min(old_size[0], new_size[0])
                        if len(param.data.size()) == 1:
                            param.data[:min_0] = old_net_dict[key].data[:min_0]
                        else:
                            min_1 = min(old_size[1], new_size[1])
                            param.data[:min_0, :min_1] = old_net_dict[key].data[:min_0, :min_1]
        return new_net

    @property
    def init_dict(self):

        init_dict = {"num_inputs": self.num_inputs, "num_outputs": self.num_outputs, "hidden_size": self.hidden_size,
                     "hidden_activation": self.hidden_activation, "output_activation": self.output_activation}
        return init_dict

    @property
    def short_dict(self):

        short_dict = {"hidden_size": self.hidden_size, "hidden_activation": self.hidden_activation, 
                    "output_activation": self.output_activation}
        return short_dict