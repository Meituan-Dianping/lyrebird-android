# Lyrebird Android plugin
[![Build Status](https://travis-ci.org/meituan/lyrebird-android.svg?branch=master)](https://travis-ci.org/meituan/lyrebird-android)
[![PyPI](https://img.shields.io/pypi/v/lyrebird-android.svg)](https://pypi.python.org/pypi/lyrebird-android)
![PyPI](https://img.shields.io/pypi/pyversions/lyrebird.svg)
![GitHub](https://img.shields.io/github/license/meituan/lyrebird-android.svg)

**[Lyrebird](https://github.com/meituan/lyrebird)是一个基于拦截以及模拟HTTP/HTTPS网络请求的面向移动应用的插件化测试平台。**

**本程序是一个Lyrebird的插件，用于支持获取Android设备信息。主要功能如下:**

* 获取当前设备信息
* 获取指定应用信息
* 获取屏幕快照
* 获取系统日志
* 获取崩溃日志
* 获取ANR日志
* 拉起指定应用

----

<img src="./image/main.png" style="width:800px">

## 环境要求

* macOS

* Python3.6及以上

* 安装[AndroidSDK](https://developer.android.com/studio/)，并设置SDK环境变量 “ANDROID_HOME”

## 安装

```bash
pip3 install lyrebird-android
```

## 启动

```bash
lyrebird
```

## 使用

使用时，通过USB线连接手机和电脑即可。

----

## 开发者指南

1. clone本项目

    ```bash
    git clone git@github.com:meituan/lyrebird-android.git
    ```

2. 进入项目目录
    
    ```bash
    cd lyrebird-android
    ```

3. 创建虚拟环境

    ```bash
    python3 -m venv venv
    ```

4. 安装依赖

    ```bash
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

5. 使用IDE打开工程（推荐[Pycharm](https://www.jetbrains.com/pycharm/)或[vscode](https://code.visualstudio.com/)）

6. debug启动应用

    使用 ./lyrebird_android/debug.py 启动

