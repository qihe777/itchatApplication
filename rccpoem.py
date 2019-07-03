import os
import pickle
import numpy as np
import tensorflow as tf


class Mypoem:
    batch_size = 1
    # 使用训练完成的模型
    model_path = "E:/DLLab/rnnmodel"

    def __init__(self):
        fr = open('E:/DLLab/all.txt', 'rb')
        self.words, self.word_num_map, self.poetrys_vector = pickle.load(fr)
        fr.close()

    # 定义RNN
    def neural_network(self, model='lstm', rnn_size=128, num_layers=2):
        tf.reset_default_graph()
        # 定义输入数据和输出目标
        input_data = tf.placeholder(tf.int32, [self.batch_size, None])
        #     output_targets = tf.placeholder(tf.int32, [batch_size, None])
        # 选择模型：传统RNN，GRU还是LSTM，默认LSTM
        if model == 'rnn':
            cell_fun = tf.contrib.rnn.BasicRNNCell
        elif model == 'gru':
            cell_fun = tf.contrib.rnn.GRUCell
        elif model == 'lstm':
            # 定义一个 LSTM 结构
            cell_fun = tf.contrib.rnn.BasicLSTMCell

            # 创建2层RNN单元，每层有128个隐藏层节点
        cell = cell_fun(rnn_size, state_is_tuple=True)
        cell = tf.contrib.rnn.MultiRNNCell([cell] * num_layers, state_is_tuple=True)

        # 提供了 zero_state 函数来生成全0的初始状态，batch_size设为64（每次取64首诗去训练）
        initial_state = cell.zero_state(self.batch_size, tf.float32)

        # 通过tf.variable_scope()指定作用域
        with tf.variable_scope('rnnlm'):

            # 通过tf.get_variable创建变量
            softmax_w = tf.get_variable("softmax_w", [rnn_size, len(self.words)])
            softmax_b = tf.get_variable("softmax_b", [len(self.words)])

            # 在tensorflow中，我们可以使用 tf.device() 指定模型运行的具体设备，可以指定运行在GPU还是CUP上，以及具体哪块
            with tf.device("/cpu:0"):
                # 这里运用embedding来将输入的不同词汇映射到隐藏层的神经元上
                embedding = tf.get_variable("embedding", [len(self.words), rnn_size])

                # tf.nn.embedding_lookup的作用就是找到要寻找的embedding中的对应的行的vector
                inputs = tf.nn.embedding_lookup(embedding, input_data)

        outputs, last_state = tf.nn.dynamic_rnn(cell, inputs, initial_state=initial_state, scope='rnnlm')
        output = tf.reshape(outputs, [-1, rnn_size])

        logits = tf.matmul(output, softmax_w) + softmax_b

        probs = tf.nn.softmax(logits)
        return logits, last_state, probs, cell, initial_state, input_data

    def gen_head_poetry(self, heads, type):
        if type != 5 and type != 7:
            print('The second para has to be 5 or 7!')
            return

        def to_word(weights):
            t = np.cumsum(weights)  # 梯形求和
            s = np.sum(weights)  # 全部和（相当于t[-1]）
            sample = int(np.searchsorted(t, np.random.rand(1) * s))
            return self.words[sample]

        _, last_state, probs, cell, initial_state, input_data = self.neural_network()
        Session_config = tf.ConfigProto(allow_soft_placement=True)
        Session_config.gpu_options.allow_growth = False

        #print("step1")
        with tf.Session(config=Session_config) as sess:
            with tf.device('/cpu:0'):
                sess.run(tf.global_variables_initializer())
                saver = tf.train.Saver(tf.global_variables())
                model_file = tf.train.latest_checkpoint(self.model_path)
                # model_file = "model/poetry.module-100"
                saver.restore(sess, model_file)
                poem = ''
                for head in heads:
                    # 如果词典中没有该词将不能产生诗句
                    if head not in self.word_num_map:
                        return "Sorry, Can't produce poem for this word --> %s" % head
                    flag = True
                    while flag:

                        state_ = sess.run(cell.zero_state(1, tf.float32))

                        x = np.array([list(map(self.word_num_map.get, u'['))])

                        [probs_, state_] = sess.run([probs, last_state],
                                                    feed_dict={input_data: x, initial_state: state_})

                        sentence = head

                        x = np.zeros((1, 1))

                        x[0, 0] = self.word_num_map[sentence]
                        [probs_, state_] = sess.run([probs, last_state],
                                                    feed_dict={input_data: x, initial_state: state_})
                        word = to_word(probs_)
                        sentence += word
                        while word != u'。':
                            x = np.zeros((1, 1))
                            x[0, 0] = self.word_num_map[word]
                            [probs_, state_] = sess.run([probs, last_state],
                                                        feed_dict={input_data: x, initial_state: state_})
                            word = to_word(probs_)
                            sentence += word
                        if len(sentence) == 2 + 2 * type:
                            sentence += u'\n'
                            poem += sentence
                            flag = False

        return poem


if __name__ == "__main__":
    x = Mypoem()
    print(x.gen_head_poetry(u'老港是猪', 5))
