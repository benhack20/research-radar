"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Settings, Database, Bell, Shield, Globe, Save, RefreshCw, Plus, Trash2, Download } from "lucide-react"
import Link from "next/link"

interface APIConfig {
  name: string
  endpoint: string
  apiKey: string
  enabled: boolean
}

interface NotificationSettings {
  newPapers: boolean
  newPatents: boolean
  scholarUpdates: boolean
  systemAlerts: boolean
  emailFrequency: "immediate" | "daily" | "weekly"
}

export default function SettingsPage() {
  const [apiConfigs, setApiConfigs] = useState<APIConfig[]>([
    {
      name: "AMiner API",
      endpoint: "https://api.aminer.cn/api",
      apiKey: "your-aminer-api-key",
      enabled: true,
    },
    {
      name: "CNKI API",
      endpoint: "https://api.cnki.net",
      apiKey: "your-cnki-api-key",
      enabled: false,
    },
  ])

  const [notifications, setNotifications] = useState<NotificationSettings>({
    newPapers: true,
    newPatents: true,
    scholarUpdates: false,
    systemAlerts: true,
    emailFrequency: "daily",
  })

  const [focusInstitutions, setFocusInstitutions] = useState<string[]>([
    "清华大学",
    "上海交通大学",
    "复旦大学",
    "同济大学",
  ])

  const [focusFields, setFocusFields] = useState<string[]>([
    "人工智能",
    "机器学习",
    "计算机视觉",
    "自然语言处理",
    "数据挖掘",
  ])

  const [newInstitution, setNewInstitution] = useState("")
  const [newField, setNewField] = useState("")

  const handleSaveSettings = () => {
    console.log("Saving settings...")
    // 这里会调用API保存设置
  }

  const handleTestAPI = (configName: string) => {
    console.log(`Testing API: ${configName}`)
    // 这里会测试API连接
  }

  const addInstitution = () => {
    if (newInstitution.trim() && !focusInstitutions.includes(newInstitution.trim())) {
      setFocusInstitutions([...focusInstitutions, newInstitution.trim()])
      setNewInstitution("")
    }
  }

  const removeInstitution = (institution: string) => {
    setFocusInstitutions(focusInstitutions.filter((i) => i !== institution))
  }

  const addField = () => {
    if (newField.trim() && !focusFields.includes(newField.trim())) {
      setFocusFields([...focusFields, newField.trim()])
      setNewField("")
    }
  }

  const removeField = (field: string) => {
    setFocusFields(focusFields.filter((f) => f !== field))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">
                首页
              </Link>
              <span className="text-gray-300">/</span>
              <h1 className="text-xl font-semibold text-gray-900">系统设置</h1>
            </div>
            <Button onClick={handleSaveSettings}>
              <Save className="h-4 w-4 mr-2" />
              保存设置
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="general" className="flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              通用
            </TabsTrigger>
            <TabsTrigger value="data" className="flex items-center">
              <Database className="h-4 w-4 mr-2" />
              数据源
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center">
              <Bell className="h-4 w-4 mr-2" />
              通知
            </TabsTrigger>
            <TabsTrigger value="focus" className="flex items-center">
              <Globe className="h-4 w-4 mr-2" />
              关注范围
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center">
              <Shield className="h-4 w-4 mr-2" />
              安全
            </TabsTrigger>
          </TabsList>

          {/* 通用设置 */}
          <TabsContent value="general">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>基本信息</CardTitle>
                  <CardDescription>配置系统的基本信息和显示设置</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="orgName">机构名称</Label>
                      <Input id="orgName" defaultValue="清华背景科技孵化器" />
                    </div>
                    <div>
                      <Label htmlFor="location">所在地区</Label>
                      <Input id="location" defaultValue="上海市杨浦区" />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="description">机构描述</Label>
                    <Textarea id="description" defaultValue="专注于数字内容生成技术的技术转移和孵化服务" rows={3} />
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="darkMode" />
                    <Label htmlFor="darkMode">启用深色模式</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="autoRefresh" defaultChecked />
                    <Label htmlFor="autoRefresh">自动刷新数据</Label>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>显示设置</CardTitle>
                  <CardDescription>自定义界面显示和数据展示方式</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="pageSize">每页显示数量</Label>
                      <Select defaultValue="20">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="10">10</SelectItem>
                          <SelectItem value="20">20</SelectItem>
                          <SelectItem value="50">50</SelectItem>
                          <SelectItem value="100">100</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="dateFormat">日期格式</Label>
                      <Select defaultValue="YYYY-MM-DD">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="YYYY-MM-DD">2024-01-15</SelectItem>
                          <SelectItem value="MM/DD/YYYY">01/15/2024</SelectItem>
                          <SelectItem value="DD/MM/YYYY">15/01/2024</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 数据源设置 */}
          <TabsContent value="data">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>API配置</CardTitle>
                  <CardDescription>配置外部数据源API接口</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {apiConfigs.map((config, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <h3 className="font-medium">{config.name}</h3>
                            <Badge variant={config.enabled ? "default" : "secondary"}>
                              {config.enabled ? "已启用" : "已禁用"}
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleTestAPI(config.name)}>
                              <RefreshCw className="h-4 w-4 mr-1" />
                              测试
                            </Button>
                            <Switch
                              checked={config.enabled}
                              onCheckedChange={(checked) => {
                                const newConfigs = [...apiConfigs]
                                newConfigs[index].enabled = checked
                                setApiConfigs(newConfigs)
                              }}
                            />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label>API端点</Label>
                            <Input
                              value={config.endpoint}
                              onChange={(e) => {
                                const newConfigs = [...apiConfigs]
                                newConfigs[index].endpoint = e.target.value
                                setApiConfigs(newConfigs)
                              }}
                            />
                          </div>
                          <div>
                            <Label>API密钥</Label>
                            <Input
                              type="password"
                              value={config.apiKey}
                              onChange={(e) => {
                                const newConfigs = [...apiConfigs]
                                newConfigs[index].apiKey = e.target.value
                                setApiConfigs(newConfigs)
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>数据同步</CardTitle>
                  <CardDescription>配置自动数据同步和更新频率</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="syncFrequency">同步频率</Label>
                      <Select defaultValue="daily">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="hourly">每小时</SelectItem>
                          <SelectItem value="daily">每日</SelectItem>
                          <SelectItem value="weekly">每周</SelectItem>
                          <SelectItem value="manual">手动</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="syncTime">同步时间</Label>
                      <Input type="time" defaultValue="02:00" />
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="autoSync" defaultChecked />
                    <Label htmlFor="autoSync">启用自动同步</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="incrementalSync" defaultChecked />
                    <Label htmlFor="incrementalSync">增量同步（仅同步新数据）</Label>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 通知设置 */}
          <TabsContent value="notifications">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>通知偏好</CardTitle>
                  <CardDescription>选择您希望接收的通知类型</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="newPapers">新论文通知</Label>
                        <p className="text-sm text-gray-500">当关注的学者发表新论文时通知</p>
                      </div>
                      <Switch
                        id="newPapers"
                        checked={notifications.newPapers}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, newPapers: checked })}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="newPatents">新专利通知</Label>
                        <p className="text-sm text-gray-500">当关注的学者申请新专利时通知</p>
                      </div>
                      <Switch
                        id="newPatents"
                        checked={notifications.newPatents}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, newPatents: checked })}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="scholarUpdates">学者信息更新</Label>
                        <p className="text-sm text-gray-500">当学者信息发生变化时通知</p>
                      </div>
                      <Switch
                        id="scholarUpdates"
                        checked={notifications.scholarUpdates}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, scholarUpdates: checked })}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label htmlFor="systemAlerts">系统警报</Label>
                        <p className="text-sm text-gray-500">系统错误和重要更新通知</p>
                      </div>
                      <Switch
                        id="systemAlerts"
                        checked={notifications.systemAlerts}
                        onCheckedChange={(checked) => setNotifications({ ...notifications, systemAlerts: checked })}
                      />
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <Label htmlFor="emailFrequency">邮件通知频率</Label>
                    <Select
                      value={notifications.emailFrequency}
                      onValueChange={(value: "immediate" | "daily" | "weekly") =>
                        setNotifications({ ...notifications, emailFrequency: value })
                      }
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="immediate">立即发送</SelectItem>
                        <SelectItem value="daily">每日汇总</SelectItem>
                        <SelectItem value="weekly">每周汇总</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 关注范围设置 */}
          <TabsContent value="focus">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>重点关注机构</CardTitle>
                  <CardDescription>设置需要重点监控的高校和研究机构</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <Input
                        placeholder="输入机构名称"
                        value={newInstitution}
                        onChange={(e) => setNewInstitution(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && addInstitution()}
                      />
                      <Button onClick={addInstitution}>
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {focusInstitutions.map((institution, index) => (
                        <Badge key={index} variant="secondary" className="flex items-center gap-1">
                          {institution}
                          <button onClick={() => removeInstitution(institution)} className="ml-1 hover:text-red-600">
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>重点关注领域</CardTitle>
                  <CardDescription>设置需要重点监控的研究领域和技术方向</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex space-x-2">
                      <Input
                        placeholder="输入研究领域"
                        value={newField}
                        onChange={(e) => setNewField(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && addField()}
                      />
                      <Button onClick={addField}>
                        <Plus className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {focusFields.map((field, index) => (
                        <Badge key={index} variant="secondary" className="flex items-center gap-1">
                          {field}
                          <button onClick={() => removeField(field)} className="ml-1 hover:text-red-600">
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>筛选条件</CardTitle>
                  <CardDescription>设置默认的数据筛选和排序条件</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="minHIndex">最小H指数</Label>
                      <Input type="number" defaultValue="10" />
                    </div>
                    <div>
                      <Label htmlFor="minCitations">最小引用数</Label>
                      <Input type="number" defaultValue="50" />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="timeRange">时间范围（年）</Label>
                    <Select defaultValue="5">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">近1年</SelectItem>
                        <SelectItem value="3">近3年</SelectItem>
                        <SelectItem value="5">近5年</SelectItem>
                        <SelectItem value="10">近10年</SelectItem>
                        <SelectItem value="all">全部</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* 安全设置 */}
          <TabsContent value="security">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>访问控制</CardTitle>
                  <CardDescription>管理系统访问权限和安全设置</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch id="requireAuth" defaultChecked />
                    <Label htmlFor="requireAuth">启用用户认证</Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="sessionTimeout" defaultChecked />
                    <Label htmlFor="sessionTimeout">会话超时保护</Label>
                  </div>

                  <div>
                    <Label htmlFor="sessionDuration">会话持续时间（小时）</Label>
                    <Input type="number" defaultValue="8" className="mt-1" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>数据安全</CardTitle>
                  <CardDescription>配置数据备份和安全策略</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch id="autoBackup" defaultChecked />
                    <Label htmlFor="autoBackup">自动数据备份</Label>
                  </div>

                  <div>
                    <Label htmlFor="backupFrequency">备份频率</Label>
                    <Select defaultValue="daily">
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">每日</SelectItem>
                        <SelectItem value="weekly">每周</SelectItem>
                        <SelectItem value="monthly">每月</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch id="encryptData" defaultChecked />
                    <Label htmlFor="encryptData">数据加密存储</Label>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>审计日志</CardTitle>
                  <CardDescription>系统操作记录和日志管理</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch id="enableAudit" defaultChecked />
                    <Label htmlFor="enableAudit">启用操作审计</Label>
                  </div>

                  <div>
                    <Label htmlFor="logRetention">日志保留期（天）</Label>
                    <Input type="number" defaultValue="90" className="mt-1" />
                  </div>

                  <Button variant="outline" className="w-full bg-transparent">
                    <Download className="h-4 w-4 mr-2" />
                    导出审计日志
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
