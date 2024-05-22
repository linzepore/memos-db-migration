# memos-db-migration
Database migration for memos

## 为什么用MySQL不用SQLite
1. 图片资源删掉之后，需要手动收缩
2. 不习惯SQLite
3. 服务器有现成的MySQL镜像，方便管理

## 为什么不用官方的
官方的貌似过期了，根据查得到的资料发现参数不对，应该是迭代了，干脆自己写一个  

![image](https://github.com/linzepore/memos-db-migration/assets/51522645/e391287a-b321-4ea3-bb71-0899608bcc3c)


## 前置条件
1. 保证新数据库是空的
2. 内存最好在2G及以上。否则很大概率会出现`Lost connection to MysoL server during query`（看数据库容器日志）
3. 当前版本是`0.22.0`（如果有变化建议先将sqlite数据库看看表是否有变化）

## 使用方式
1. docker容器添加镜像环境参数：
   ```
   - MEMOS_DRIVER=mysql
   - MEMOS_DSN=memos:password@tcp(localhost)/memos
   ```
2. 启动memo，初始化数据库的表，然后清空表数据（推荐用navicat来做）
3. 准备好sqlite数据库文件、数据库连接参数（可以是同一网络下MySQL的内网地址，docker容器也一样）
4. 填入`.py`文件中关键参数，其中`tables`参数要换成实际的表名，执行脚本
5. （可选）如果资源异常，确保环境参数下数据库已换成mysql驱动之后重建容器
