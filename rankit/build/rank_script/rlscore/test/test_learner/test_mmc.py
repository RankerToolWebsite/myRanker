
import random
random.seed(100)
import unittest

import numpy as np

from rankit.build.rank_script.rlscore.learner.steepest_descent_mmc import SteepestDescentMMC as MMC
#from rankit.build.rank_script.rlscore.learner.steepest_descent_mmc_alt import SteepestDescentMMC as MMC
#from rankit.build.rank_script.rlscore.learner.mmc import MMC as MMC


class TestCallback(object):
    def __init__(self):
        pass
    
    def callback(self, learner):
        #vis.plotResultsMultiClassMMC2D(plt, Xmat, learner.Y, fixedindices = None)
        #time.sleep(1)
        print(learner.classcounts)

def generate_2d_gaussian_clusters(num, mux, muy, var, seed=None):
    Y = []
    X = []
    if seed is not None:
        random.seed(seed)
    for j in range(len(num)):
        for i in range(num[j]):
            # Generate "random" order of samples
            x = random.gauss(mux[j],var[j])
            y = random.gauss(muy[j],var[j])
            X.append([x,y])
            Y.append(j)
    
    return Y, X


def dotesting(ppc = 400):
        classcount = 3 #Number of clusters
        #ppc = 400 #Points per Gaussian (not cluster)
        #Generate data
        #Y,X = gen.generate([ppc,ppc],[10,10], [10,20],[2,2])
        Y, X = generate_2d_gaussian_clusters([ppc, ppc, ppc], [10, 10, 20], [10, 20, 15], [2, 2, 2])
        X = np.array(X)
        print(X.shape)

    
        
        bvecs = random.sample(range(ppc), 100)
        
        kwargs = {}
        kwargs['X'] = X
        kwargs['regparam'] = '1'
        kwargs['kernel'] = 'GaussianKernel'
        kwargs['gamma'] = 2. ** (-20.)
        kwargs['bias'] = 1
        kwargs['number_of_clusters'] = classcount
        kwargs['regparam'] = 2. ** (-30.)
        #kwargs['learner'] = 'MMC'
        kwargs['basis_vectors'] = X[bvecs]
        

        tcb = TestCallback()
        kwargs['callback'] = tcb
        
        #mselector = None
        mmc = MMC(**kwargs)
        #mmc = SteepestDescentMMC.createLearner(**kwargs)
        #trainresults = core.trainModel(**kwargs)
        #model = trainresults['model']
        #writer.write_ints('./examples/predictions/clusters.txt', trainresults['predicted_clusters_for_training_data'])

class Test(unittest.TestCase):
    
    def test_mmc(self):
        dotesting()


if __name__=="__main__":
    import cProfile
    #dotesting()
    cProfile.run('dotesting(1500)')

