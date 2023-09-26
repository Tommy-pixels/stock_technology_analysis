import talib
import numpy

close = numpy.random.random(100)

output = talib.MOM(close, timeperiod=5)
print(output)