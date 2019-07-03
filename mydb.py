import pymysql


class mysql:

    def __init__(self):
        try:
            self.connect = pymysql.connect(host='127.0.0.1', port=3306, user='qihe', passwd='zhangyinqi', db='wechat',
                                           charset='utf8')
        except Exception as e:
            print(e)

    def insert(self, id, usrname, time, message):
        # 创建游标，查询获得的数据以 字典（dict） 形式返回
        cursor = self.connect.cursor()
        # 执行SQL语句，插入数据到 test 表，栏位名称为 name,value
        cursor.execute('insert into send value({},"{}",{},"{}")'.format(id, usrname, time, message))
        # 向数据库提交执行的语句
        self.connect.commit()
        # 关闭游标
        cursor.close()

    # 以元组的形式返回数据
    def select(self, usrname):
        cousor = self.connect.cursor()
        # 获取数据库游标对象
        sql = 'SELECT * FROM send where usrname ="{}";'.format(usrname)
        # 用一个变量接收mysql语句
        cousor.execute(sql)
        # 执行
        result = cousor.fetchall()
        # 取结果集剩下所有行
        cousor.close()
        return result

    def selectall(self):
        cousor = self.connect.cursor()
        # 获取数据库游标对象
        sql = 'SELECT * FROM send;'
        # 用一个变量接收mysql语句
        cousor.execute(sql)
        # 执行
        result = cousor.fetchall()
        # 取结果集剩下所有行
        cousor.close()
        return result

    def delet(self, myid):
        cursor = self.connect.cursor()
        # SQL 删除语句
        sql = "DELETE FROM send WHERE id = %s" % myid
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 提交修改
            self.connect.commit()
        except:
            # 发生错误时回滚
            self.connect.rollback()

    def selectMovie(self, start, end):
        cousor = self.connect.cursor()
        # 获取数据库游标对象
        sql = 'SELECT * FROM movierank where id >{} and id<{};'.format(start, end)
        # 用一个变量接收mysql语句
        cousor.execute(sql)
        # 执行
        result = cousor.fetchall()
        # 取结果集剩下所有行
        cousor.close()
        return result
