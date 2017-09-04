# Get tensorflow to do something.

import twcr
import tensorflow as tf

t1=twcr.get_slice_at_hour('prmsl',1915,3,12,6,version='4.1.8')
t2=twcr.get_slice_at_hour('prmsl',1915,3,12,12,version='4.1.8')

t3 = tf.subtract(t2.data,t1.data)
t4 = tf.reduce_mean(t3,0)

sess = tf.Session()
result=sess.run(t4)

