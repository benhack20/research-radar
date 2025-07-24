"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Users, FileText, Award, TrendingUp, Plus, Settings, Download } from "lucide-react"
import Link from "next/link"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"

interface DashboardStats {
  totalScholars: number
  totalPapers: number
  totalPatents: number
  recentUpdates: number
  totalScholarsMoM: number
  totalPapersMoM: number
  totalPatentsMoM: number
}

interface Activity {
  id: number;
  type: 'scholar' | 'paper' | 'patent';
  action: string;
  name: string;
  time: string;
  owner_name?: string;
}

export default function HomePage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalScholars: 0,
    totalPapers: 0,
    totalPatents: 0,
    recentUpdates: 0,
    totalScholarsMoM: 0,
    totalPapersMoM: 0,
    totalPatentsMoM: 0,
  })

  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false)
  const [activities, setActivities] = useState<Activity[]>([])

  useEffect(() => {
    fetch("/api/dashboard/stats", {
      headers: {
        Authorization: "Basic " + btoa("admin:admin"),
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setStats({
          totalScholars: data.totalScholars,
          totalPapers: data.totalPapers,
          totalPatents: data.totalPatents,
          recentUpdates: data.recentUpdates,
          totalScholarsMoM: data.totalScholarsMoM,
          totalPapersMoM: data.totalPapersMoM,
          totalPatentsMoM: data.totalPatentsMoM,
        })
      })
      .catch(() => {
        setStats({
          totalScholars: 0,
          totalPapers: 0,
          totalPatents: 0,
          recentUpdates: 0,
          totalScholarsMoM: 0,
          totalPapersMoM: 0,
          totalPatentsMoM: 0,
        })
      })
  }, [])

  useEffect(() => {
    fetch("/api/activities", {
      headers: {
        Authorization: "Basic " + btoa("admin:admin"),
      },
    })
      .then((res) => res.json())
      .then((data) => setActivities(data))
      .catch(() => setActivities([]))
  }, [])

  const quickActions = [
    {
      title: "学者检索",
      description: "查看和管理学者信息",
      icon: Users,
      href: "/scholars",
      color: "bg-blue-500",
    },
    {
      title: "论文专利",
      description: "浏览论文和专利数据",
      icon: FileText,
      href: "/research",
      color: "bg-green-500",
    },
    {
      title: "新增学者",
      description: "添加新的学者到系统",
      icon: Plus,
      href: "/scholars?action=add",
      color: "bg-purple-500",
    },
    {
      title: "系统设置",
      description: "配置系统参数",
      icon: Settings,
      href: "/settings",
      color: "bg-gray-500",
    },
  ]

  const recentActivities = [
    { type: "scholar", name: "张教授", action: "新增", time: "2小时前" },
    { type: "paper", name: "AI在医疗诊断中的应用", action: "更新", time: "4小时前" },
    { type: "patent", name: "智能传感器系统", action: "新增", time: "6小时前" },
    { type: "scholar", name: "李研究员", action: "更新", time: "1天前" },
  ]

  // 智能解析活动名称
  function getDisplayName(activity: Activity) {
    // 专利title后端已保证是字符串，直接返回
    return activity.name;
  }

  // 活动描述
  function getActivityDesc(activity: Activity) {
    if (activity.type === 'scholar') {
      return `学者：${activity.name}`;
    }
    if (activity.type === 'paper') {
      return `论文：${getDisplayName(activity)}`;
    }
    if (activity.type === 'patent') {
      return `专利：${getDisplayName(activity)}`;
    }
    return getDisplayName(activity);
  }

  return (
    <>
      <Dialog open={settingsDialogOpen} onOpenChange={setSettingsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>提示</DialogTitle>
            <DialogDescription>设置功能暂未开放，敬请期待！</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">科研成果雷达系统</h1>
                <Badge variant="secondary" className="ml-3">
                  技术转移专用
                </Badge>
              </div>
              <div className="flex items-center space-x-4">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  导出报告
                </Button>
                <Button variant="ghost" size="sm" onClick={() => setSettingsDialogOpen(true)}>
                  <Settings className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 统计概览 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">学者总数</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalScholars}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.totalScholarsMoM > 0 && `+${stats.totalScholarsMoM}% 较上月`}
                  {stats.totalScholarsMoM < 0 && `${stats.totalScholarsMoM}% 较上月`}
                  {stats.totalScholarsMoM === 0 && '持平'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">论文总数</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalPapers}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.totalPapersMoM > 0 && `+${stats.totalPapersMoM}% 较上月`}
                  {stats.totalPapersMoM < 0 && `${stats.totalPapersMoM}% 较上月`}
                  {stats.totalPapersMoM === 0 && '持平'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">专利总数</CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalPatents}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.totalPatentsMoM > 0 && `+${stats.totalPatentsMoM}% 较上月`}
                  {stats.totalPatentsMoM < 0 && `${stats.totalPatentsMoM}% 较上月`}
                  {stats.totalPatentsMoM === 0 && '持平'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">近期更新</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.recentUpdates}</div>
                <p className="text-xs text-muted-foreground">今日新增</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
            {/* 快速操作 */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>快速操作</CardTitle>
                  <CardDescription>选择下方操作快速访问系统功能</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {quickActions.map((action, index) => {
                      if (action.href === "/settings") {
                        return (
                          <div key={index} onClick={() => setSettingsDialogOpen(true)} style={{ cursor: "pointer" }}>
                            <Card className="hover:shadow-md transition-shadow">
                              <CardContent className="p-6">
                                <div className="flex items-center space-x-4">
                                  <div className={`p-3 rounded-lg ${action.color}`}>
                                    <action.icon className="h-6 w-6 text-white" />
                                  </div>
                                  <div>
                                    <h3 className="font-semibold">{action.title}</h3>
                                    <p className="text-sm text-muted-foreground">{action.description}</p>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        )
                      }
                      return (
                        <Link key={index} href={action.href}>
                          <Card className="hover:shadow-md transition-shadow cursor-pointer">
                            <CardContent className="p-6">
                              <div className="flex items-center space-x-4">
                                <div className={`p-3 rounded-lg ${action.color}`}>
                                  <action.icon className="h-6 w-6 text-white" />
                                </div>
                                <div>
                                  <h3 className="font-semibold">{action.title}</h3>
                                  <p className="text-sm text-muted-foreground">{action.description}</p>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </Link>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* 最近活动 */}
            <div className="h-full">
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>最近活动</CardTitle>
                  <CardDescription>系统最新的数据更新记录</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activities.length === 0 && <div className="text-gray-400 text-sm">暂无活动</div>}
                    {activities.map((activity, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          {activity.type === "scholar" && (
                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <Users className="h-4 w-4 text-blue-600" />
                            </div>
                          )}
                          {activity.type === "paper" && (
                            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                              <FileText className="h-4 w-4 text-green-600" />
                            </div>
                          )}
                          {activity.type === "patent" && (
                            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                              <Award className="h-4 w-4 text-purple-600" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">{getActivityDesc(activity)}</p>
                          <p className="text-sm text-gray-500">
                            {activity.action} • {new Date(activity.time).toLocaleString("zh-CN", { hour12: false })}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
