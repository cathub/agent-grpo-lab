"""Descriptive exact binomial and paired stratified task-bootstrap intervals."""
import math
import random
from functools import lru_cache


@lru_cache(None)
def log_coefficients(n):
    return tuple(math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1) for j in range(n+1))


def cdf(n,k,p):
    if p<=0:return 1.0
    if p>=1:return float(k>=n)
    lp,lq=math.log(p),math.log1p(-p)
    return min(1.0,math.fsum(math.exp(c+j*lp+(n-j)*lq) for j,c in enumerate(log_coefficients(n)) if j<=k))


def cdf_inverse(n,k,q):
    lo,hi=0.0,1.0
    for _ in range(60):
        mid=(lo+hi)/2
        if cdf(n,k,mid)>q:lo=mid
        else:hi=mid
    return (lo+hi)/2


def clopper_pearson(k,n,alpha=0.05):
    if not 0<=k<=n or n<1:raise ValueError('Invalid binomial counts')
    return [0.0 if k==0 else cdf_inverse(n,k-1,1-alpha/2),
            1.0 if k==n else cdf_inverse(n,k,alpha/2)]


def quantile(values,q):
    values=sorted(values);position=(len(values)-1)*q;i=int(position)
    return values[i] if i==len(values)-1 else values[i]+(values[i+1]-values[i])*(position-i)


def paired_task_bootstrap(before,after,tasks,iterations=5000,seed=20261121):
    """Resample paired task means, stratified by category/split; retain 16 seeds.

    This is task-level uncertainty conditional on this small task inventory,
    not an IID bootstrap of individual rollouts or a guarantee for unseen tasks.
    """
    if before.keys()!=after.keys():raise ValueError('Task IDs differ')
    strata={}
    for key in sorted(before):
        task=tasks[key];strata.setdefault((task['category'],task['split']),[]).append(key)
    rng=random.Random(seed);samples=[]
    for _ in range(iterations):
        selected=[rng.choice(ids) for ids in strata.values() for _ in ids]
        samples.append(sum(after[key]-before[key] for key in selected)/len(selected))
    return {'delta':sum(after[k]-before[k] for k in before)/len(before),
        'ci95':[quantile(samples,.025),quantile(samples,.975)],
        'iterations':iterations,'seed':seed,'tasks':len(before),
        'method':'paired stratified task-cluster percentile bootstrap; all seed outcomes retained in task means'}
