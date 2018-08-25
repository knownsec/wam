## WAM Wiki
---

### 应用监控 (App Monitor)

主要用于显示和管理 "厂商"、"应用下载规则"、"更新比较结果"、"应用包下载"等。要对某网络应用进行源码监控，需要添加相应下载规则后，守护进程才能读取规则数据对其进行下载并监控。

#### 厂商/规则 信息管理

登录后，通过侧栏进入 `AM` 模块，然后切换标签至 `Rules` 页面 (`/am/rules`)，点击 `Add re` 按钮添加规则。这里需要说明的是，每一个应用都属于某个厂商，因此为了方便管理和统计，需要为每一条规则指定相应的厂商，添加规则前若不存在其所属的厂商，则点击 `Add re` 添加按钮后首先选择 `Add a vendor` 进行厂商信息编辑，说明如下图：

![](/documents/wiki_imgs/1.png)

厂商信息详细说明：

* `Vendor Name` - 厂商名称，如 Discuz，WordPress，ThinkPHP 等
* `Website` - 厂商官方主页，如 WordPress 官方站点为 http://www.wordpress.com
* `Description` - 厂商描述信息
* `Logo` - 厂商 Logo 用于页面更好的展示和区分信息

下面，以 `WordPress` 为例，添加一个名为 `WordPress` 的厂商，填好信息如下：

![](/documents/wiki_imgs/2.png)

然后点击提交，若信息无误则会自动刷新页面，切换标签至 `Vendors` 页面 (`/am/vendor`)，即可看到新增了一项厂商信息 (表格内容在后面进行详细说明)。

![](/documents/wiki_imgs/3.png)

添加好厂商信息后，我们就可以回到 `Rules` 页面开始添加需要监控的应用下载规则，同样是点击 `Add re` 按钮，然后选择 `Or add rule` 进行下载规则编辑，说明如下图：

![](/documents/wiki_imgs/4.png)

下载规则信息详细说明：

* `Vendor` - 下载规则所属厂商，例如该监控应用属于 WordPress 厂商旗下，则在这里选择 WordPress 即可
* `Rule Name` - 下载规则名称，用于标识每一条规则，例如我们需要监控中文版的 WordPress UTF8编码的应用，则在这里可以填写为 WordPress_CN_UTF8
* `Source Url` - 固定应用下载链接或者下载链接所在的入口地址，例如 sqlmap 在 GitHub 上有固定的下载链接(https://github.com/sqlmapproject/sqlmap/archive/master.zip)，直接将固定下载链接填写在此处即可。若不存在固定下载链接，则需要同时填写下载入口地址和下面要编辑的正则匹配规则，如 Discuz 下载页面(http://www.comsenz.com/downloads/install/discuzx)，需要添加简体UTF-8的应用的监控规则，在此处填写好下载入口地址后，转到下栏编辑匹配正则
* `Regular Expression` - 下载链接匹配规则，在没有固定下载链接时需要编辑的项。如上所说需要从 Discuz 下载页面中匹配出简体UTF-8版本的应用下载链接，通过查看源码可以得到下载链接匹配规则为 `href="(?P<download_url>.*UTF8.zip)\s"`，将其填写在此处即可，需要注意的时匹配的内容需要使用别名 `download_url` 进行标注

下面，添加一条 `WordPress` 中文版应用下载规则，将其命名为 `WordPress_zh_CN`，并填写相关信息：

![](/documents/wiki_imgs/5.png)

提交后，自动刷新页面，若出错则会出现错误提示。在 `Rules` 页面可以查看到所有的规则信息：

![](/documents/wiki_imgs/6.png)

添加完成后，监控守护进程就能读取到其下载规则进行监控流程。在 `Rules` 页面可以实时编辑厂商信息和规则信息，通过点击厂商或者规则名称即可。

若需要删除某条规则，点击规则信息左侧的 `Delete` 红色按钮即可：

![](/documents/wiki_imgs/7.png)

#### 更新推送

当一个应用下载规则所对应的网络应用包实时更新并且被监控守护进程识别到后，会在 `AM Index` 标签页实时地显示出来，如下图：

![](/documents/wiki_imgs/11.png)

若需直接查看对应的 DIff 详情，点击每条信息右边所对应的链接即可。关于 Diff 详情页面在后面进行说明。

#### Diff结果 详情/管理

登录后，通过侧栏进入 `AM` 模块，然后切换标签至 `Diff` 页面 (`/am/diff`)，可以看到所有的 Diff 记录，包括了每一条 Diff 结果对应的规则名称、源包和目标包、添加时间、由分析器检测到的漏洞类型 tag、详情按钮：

![](/documents/wiki_imgs/8.png)

若需要下载对应的应用包，点击源包或者目标包名称即可进行下载。若需要查看 Diff 详情，点击每条记录最右边的 `Detail` 按钮即可进入详情页面：

![](/documents/wiki_imgs/9.png)

在 Diff 详情页面可以看到此次 Diff 分析的结构，若在 Diff 结果中有检测可能存在的漏洞，则会在标签 `Tags` 处显示出来，点击漏洞标签可以弹出具体的分析器检测结果，包括了触发该漏洞匹配规则所在的文件、行数、描述等：

![](/documents/wiki_imgs/10.png)

在 Diff 详情页面可以对本次的所有 Diff 输出进行浏览和分析。

#### 厂商统计

在 `AM` 模块中切换标签至 `Vendors` 页面 (`/am/vendor`)，即可看到数据库中所有的厂商信息，包括每个厂商的名称、官方站点、库中规则数、Diff总数等。

![](/documents/wiki_imgs/12.png)

点击对应的厂商名称，进入厂商的详细页面：

![](/documents/wiki_imgs/13.png)

在详情页面，会显示出厂商的一些基本信息：Logo，名称，站点和简介。中间是一个统计图表，用于直观的显示一年中该厂商的所有规则所产生的 Diff 总数以及由分析器所检测出来的对应漏洞数。通过统计图表可以非常直观地看出该厂商的整体趋势和常见漏洞类型的趋势，方便后续分析和输出报表。

最下面是该厂商的所有 Diff 记录，功能同 `Diff` 页面相同。

