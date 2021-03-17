import pandas as pd
import numpy as np
import torch
from glycowork.glycan_data.loader import lib
from glycowork.ml.processing import dataset_to_dataloader

try:
  from torch_geometric.data import Data, DataLoader
except ImportError:
    raise ImportError('<torch_geometric missing; cannot do deep learning>')

def glycans_to_emb(glycans, model, libr = None, batch_size = 32, rep = True):
    """returns a dataframe of learned representations for a list of glycans\n
    glycans -- list of glycans in IUPACcondensed; strings\n
    model -- trained graph neural network (such as SweetNet) for analyzing glycans\n
    libr -- sorted list of unique glycoletters observed in the glycans of our dataset\n
    batch_size -- change to batch_size used during training; default is 32\n
    rep -- True returns representations, False returns actual predicted labels; default is True\n

    returns dataframe of learned representations (columns) for each glycan (rows)
    """
    if libr is None:
      libr = lib
    glycan_loader = dataset_to_dataloader(glycans, range(len(glycans)),
                                          libr = libr, batch_size = batch_size,
                                          shuffle = False)
    res = []
    for data in glycan_loader:
        x, y, edge_index, batch = data.x, data.y, data.edge_index, data.batch
        x = x.cuda()
        y = y.cuda()
        edge_index = edge_index.cuda()
        batch = batch.cuda()
        model = model.eval()
        pred, out = model(x, edge_index, batch, inference = True)
        if rep:
            res.append(out)
        else:
            res.append(pred)
    res2 = [res[k].detach().cpu().numpy() for k in range(len(res))]
    res2 = pd.DataFrame(np.concatenate(res2))
    return res2
