import unittest
from src.capability_uncertainty import clopper_pearson,paired_task_bootstrap


class UncertaintyTests(unittest.TestCase):
    def test_exact_binomial_known_boundaries(self):
        self.assertAlmostEqual(clopper_pearson(0,10)[1],1-.025**.1,places=10)
        self.assertAlmostEqual(clopper_pearson(10,10)[0],.025**.1,places=10)
        a,b=clopper_pearson(5,10)
        self.assertAlmostEqual(a,.1870860284,places=9)
        self.assertAlmostEqual(b,.8129139716,places=9)

    def test_paired_cluster_reproduction_and_zero_contrast(self):
        tasks={'a':{'category':'x','split':'train'},'b':{'category':'x','split':'train'}}
        before={'a':0.,'b':1.};after={'a':1.,'b':0.}
        a=paired_task_bootstrap(before,after,tasks,iterations=100)
        self.assertEqual(a,paired_task_bootstrap(before,after,tasks,iterations=100))
        self.assertEqual(a['delta'],0)
        self.assertEqual(paired_task_bootstrap(before,before,tasks,iterations=100)['ci95'],[0.,0.])
