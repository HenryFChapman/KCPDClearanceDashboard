from KarpelStarter import karpelStarter
from dataGatherer import dataGatherer
from dataCleaner import dataCleaner

dataGatherer()

karpelCases = karpelStarter()

dataCleaner(karpelCases)