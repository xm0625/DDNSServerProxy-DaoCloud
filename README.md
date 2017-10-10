# DDNSServerProxy #

部分地区实施域名审查(NJ网警), 3322DDNS上报接口躺枪, 利用DaoCloud免费的服务资源做一个Proxy服务

### 简介 ###

* 通过DaoCloud进行3322DDNS上报接口的转发, 绕开域名审查对上报接口的限制.
* 绕过DaoCloud免费的服务资源每24小时自动关闭的限制

### 如何部署? ###

* fork代码到你的Github
* 注册一个DaoCloud账号
* 将账号与你的Github绑定
* 创建项目并选择刚刚fork的仓库
* 手动触发构建, 获得镜像
* 部署镜像的最新版本到云端测试环境
* 添加一个8090端口的http外部访问
* 点击高级设置, 部署后启动选择否, 点击部署
* 地址栏中https://dashboard.daocloud.io/apps/xxxx, xxxx即为APP_ID
* 部署完成后, 去个人中心-API记下你的API Token
* 回到应用的配置页, 自定义环境变量中添加两个变量, APP_ID和API_TOKEN, 值在上面两步已经获得. 保存更改
* 启动应用. 等待启动完成后, "访问地址"已经可以提供服务.类似http://xxxx.daoapp.io

### 客户端如何使用? ###

* 更新DDNS ip 的URL为 http://xxxx.daoapp.io/?hostname=<你的域名>&user=<你的用户名>&password=<你的密码>
* 替换http://xxxx.daoapp.io 为你的"访问地址"
* 替换<...>为你自己的信息
* 可以使用 wget 'http://xxxx.daoapp.io/?hostname=<你的域名>&user=<你的用户名>&password=<你的密码>' 来更新
* 可以加入到crontab定期执行
