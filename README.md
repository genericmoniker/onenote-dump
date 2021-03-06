
# Onenote转为Markdown文本
## Requirement
- `Python 3`
- `Some Packages`

## 1. Overview
在github上看到一个项目，是将Onenote笔记转为Markdown文本的。将Onenote转换成Markdown后，可以将自己的Onenote笔记发布在CSDN、github等平台。我自己几乎所有的笔记都是在Onenote上，所以看到这个项目觉得很好用，分享给大家。

github项目地址：https://github.com/HuimingPan/onenote-dump

## 2.Illustration
1. 配置环境。主要是需要安装`Python`和一些包，具体需要哪些包可以在使用程序转换程序 `onenote-dump` 后根据错误提示来安装。建议在Anaconda创建一个新的环境，然后再Anaconda中打开Terminal。需要的库在Anaconda中都有。
2. 打开命令提示符(cmd.exe)，将目录转换到"onenote-dump"文件夹的上一级目录，也就是如图所示位置；
![在这里插入图片描述](https://img-blog.csdnimg.cn/2021030613484418.png)

3. 在 `cmd`中输入命令：
    
    ```
    python onenote-dump <notebook> <output directory>
    ```
    其中，“notebook”——笔记本名；“output directory”——文档输出地址；
    比如：

    ```
    python onenote-dump "Software Development Notes" C:\Temp\dump
    ```
4. 授权
    在运行上述命令后，会打开一个浏览器页面，输入自己的Microsoft账号和密码，使脚本有权访问Onedrive中的有关笔记本。在第一次授权之后，可以不需要再次授权。
5. 笔记转换
    授权完成后，程序将会将你的笔记本转换承.md文件，并保存在`<output directory>`处。

## 3.Attention
- 每一个md文件是一个Onenote页，而非一整个笔记本或者分区；
- 程序对公式的转换性能不佳。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210305165523398.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NjE5MTAzMw==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210305170243269.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NjE5MTAzMw==,size_16,color_FFFFFF,t_70)
