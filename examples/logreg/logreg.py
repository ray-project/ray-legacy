import orchpy as op
import numpy as np
import tensorflow as tf

# build computation graph

W = tf.Variable(tf.zeros([784, 2]))
b = tf.Variable(tf.zeros([2]))

x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 2])

y = tf.nn.softmax(tf.matmul(x, W) + b)

cross_entropy = -tf.reduce_sum(y_ * tf.log(y))

train_step = tf.train.GradientDescentOptimizer(0.001).minimize(cross_entropy)

init = tf.initialize_all_variables()

sess = tf.Session()
sess.run(init)

@op.distributed([int, int], [np.ndarray])
def random_onehot(num_data, num_classes):
  index = np.random.randint(0, num_classes, size=num_data)
  data = np.zeros((num_data, num_classes), dtype="float32")
  data[np.arange(num_data), index] = 1.0
  return data

@op.distributed([np.ndarray, np.ndarray, np.ndarray, np.ndarray], [np.ndarray, np.ndarray])
def train(W_new, b_new, X_data, y_data):
  for
  W.assign(Wnew)
  b.assign(bnew)
  sess.run(train_step, feed_dict={x: Xdata, y_: ydata})
  return sess.run(W), sess.run(b)

@op.distributed([np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, float], [np.ndarray, np.ndarray])
def train(W_init, b_init, X_refs, y_refs, tau, precision, num_workers):
  W.assign(W_init)
  b.assign(b_init)
  assert X_refs.shape[0] == y_refs.shape[0]
  n = X_refs.shape[0]
  while sess.run(cross_entropy) > precision:
    indices = [np.choice(n, tau) for i in range(num_workers)]
    for i in range(num_workers):
      indices = np.choice(n, tau)
