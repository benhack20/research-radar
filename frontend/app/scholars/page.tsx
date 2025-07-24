"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Search, Plus, Filter, Download, MapPin, GraduationCap, ExternalLink, Globe, Eye, Users } from "lucide-react"
import Link from "next/link"
import type { Scholar } from "../types/api-types"

export default function ScholarsPage() {
  const [scholars, setScholars] = useState<Scholar[]>([])
  const [filteredScholars, setFilteredScholars] = useState<Scholar[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedAffiliation, setSelectedAffiliation] = useState<string>("all")
  const [selectedNation, setSelectedNation] = useState<string>("all")
  const [hIndexRange, setHIndexRange] = useState<[number, number]>([0, 100])
  const [citationRange, setCitationRange] = useState<[number, number]>([0, 10000])
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [addScholarName, setAddScholarName] = useState("")

  // 模拟真实数据
  useEffect(() => {
    const mockScholars: Scholar[] = [
      {
        id: "56066a5245cedb339687488b",
        name: "Chun Yu",
        name_zh: "喻纯",
        avatar: "https://static.aminer.cn/upload/avatar/511/1134/1665/56066a5245cedb339687488b_0.jpg",
        nation: "China",
        bind: false,
        indices: {
          activity: 119.2335,
          citations: 3211,
          diversity: 2.7321,
          gindex: 49,
          hindex: 32,
          newStar: 15.0327,
          pubs: 227,
          risingStar: 15.0327,
          sociability: 6.0186,
        },
        profile: {
          address: "Room 3-526, Building FIT, Tsinghua University, Beijing",
          affiliation:
            "Pervasive Interaction Lab, Institute of HCI and Media Integration, Department of Computer Science and Technology, Tsinghua University",
          affiliation_zh: "清华大学计算机科学与技术系人机交互与媒体集成研究所",
          bio_zh:
            "研究方向是人机交互，其研究围绕人机交互自然性的计算原理和优化方法开展，具有重要的理论和实际应用价值。",
          position: "Associate Professor",
          position_zh: "副教授",
          homepage: "http://pi.cs.tsinghua.edu.cn/lab/people/ChunYu/",
          gender: "male",
        },
        tags: [
          "Text Entry",
          "Virtual Reality",
          "Computer Science",
          "Accessibility",
          "Smart Home",
          "Gesture Recognition",
          "Large Language Models",
        ],
        tags_score: [21, 17, 8, 7, 7, 7, 7],
        tags_zh: ["性能评估", "旋转手势", "佩戴位置", "旋转模式", "平坦区段", "惯性传感器"],
        links: {
          gs: {
            type: "gs",
            url: "https://scholar.google.com.hk/citations?hl=zh-CN&user=7LwMFFAAAAAJ",
          },
          resource: {
            resource_link: [
              {
                id: "hp",
                url: "https://www.cs.tsinghua.edu.cn/info/1117/3539.htm",
              },
              {
                id: "dblp",
                url: "https://dblp.uni-trier.de/pid/72/6319.html",
              },
            ],
          },
        },
        num_followed: 2,
        num_viewed: 1232,
        num_upvoted: 0,
      },
    ]
    setScholars(mockScholars)
    setFilteredScholars(mockScholars)
  }, [])

  // 筛选逻辑
  useEffect(() => {
    const filtered = scholars.filter((scholar) => {
      const matchesSearch =
        scholar.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (scholar.name_zh && scholar.name_zh.includes(searchTerm)) ||
        scholar.profile.affiliation.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (scholar.profile.affiliation_zh && scholar.profile.affiliation_zh.includes(searchTerm))

      const matchesAffiliation =
        selectedAffiliation === "all" ||
        scholar.profile.affiliation.includes(selectedAffiliation) ||
        (scholar.profile.affiliation_zh && scholar.profile.affiliation_zh.includes(selectedAffiliation))

      const matchesNation = selectedNation === "all" || scholar.nation === selectedNation

      const matchesHIndex = scholar.indices.hindex >= hIndexRange[0] && scholar.indices.hindex <= hIndexRange[1]

      const matchesCitations =
        scholar.indices.citations >= citationRange[0] && scholar.indices.citations <= citationRange[1]

      return matchesSearch && matchesAffiliation && matchesNation && matchesHIndex && matchesCitations
    })

    setFilteredScholars(filtered)
  }, [scholars, searchTerm, selectedAffiliation, selectedNation, hIndexRange, citationRange])

  const exportData = () => {
    console.log("Exporting scholars data...")
  }

  const uniqueAffiliations = Array.from(
    new Set([
      ...scholars.map((s) => s.profile.affiliation),
      ...scholars.map((s) => s.profile.affiliation_zh).filter(Boolean),
    ]),
  )
  const uniqueNations = Array.from(new Set(scholars.map((s) => s.nation).filter(Boolean)))

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
              <h1 className="text-xl font-semibold text-gray-900">学者检索</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Button onClick={exportData} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                导出数据
              </Button>
              <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    新增学者
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>新增学者</DialogTitle>
                    <DialogDescription>输入学者姓名，系统将自动搜索AMiner数据库</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <Input
                      placeholder="请输入学者姓名（中文或英文）"
                      value={addScholarName}
                      onChange={(e) => setAddScholarName(e.target.value)}
                    />
                    <Button className="w-full">搜索学者</Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 筛选区域 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              筛选条件
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">搜索</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="姓名、机构..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">机构</label>
                <Select value={selectedAffiliation} onValueChange={setSelectedAffiliation}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择机构" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部机构</SelectItem>
                    <SelectItem value="清华大学">清华大学</SelectItem>
                    <SelectItem value="北京大学">北京大学</SelectItem>
                    <SelectItem value="上海交通大学">上海交通大学</SelectItem>
                    <SelectItem value="复旦大学">复旦大学</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">国家/地区</label>
                <Select value={selectedNation} onValueChange={setSelectedNation}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择国家" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部国家</SelectItem>
                    <SelectItem value="China">中国</SelectItem>
                    <SelectItem value="USA">美国</SelectItem>
                    <SelectItem value="UK">英国</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">H指数范围</label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={hIndexRange[0]}
                    onChange={(e) => setHIndexRange([Number.parseInt(e.target.value) || 0, hIndexRange[1]])}
                    className="w-20"
                  />
                  <span>-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={hIndexRange[1]}
                    onChange={(e) => setHIndexRange([hIndexRange[0], Number.parseInt(e.target.value) || 100])}
                    className="w-20"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">引用数范围</label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={citationRange[0]}
                    onChange={(e) => setCitationRange([Number.parseInt(e.target.value) || 0, citationRange[1]])}
                    className="w-20"
                  />
                  <span>-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={citationRange[1]}
                    onChange={(e) => setCitationRange([citationRange[0], Number.parseInt(e.target.value) || 10000])}
                    className="w-20"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 结果统计 */}
        <div className="flex justify-between items-center mb-6">
          <p className="text-sm text-gray-600">
            共找到 <span className="font-semibold">{filteredScholars.length}</span> 位学者
          </p>
        </div>

        {/* 学者卡片网格 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredScholars.map((scholar) => (
            <Card key={scholar.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-4">
                <div className="flex items-start space-x-4">
                  <Avatar className="w-16 h-16">
                    <AvatarImage src={scholar.avatar || "/placeholder.svg"} alt={scholar.name} />
                    <AvatarFallback className="text-lg font-semibold">
                      {scholar.name_zh ? scholar.name_zh.charAt(0) : scholar.name.charAt(0)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <CardTitle className="text-xl">{scholar.name_zh || scholar.name}</CardTitle>
                      {scholar.nation && (
                        <Badge variant="outline" className="text-xs">
                          {scholar.nation}
                        </Badge>
                      )}
                    </div>
                    {scholar.name_zh && <p className="text-sm text-gray-500 mb-2">{scholar.name}</p>}
                    <div className="flex items-center text-sm text-gray-600 mb-2">
                      <GraduationCap className="h-4 w-4 mr-1" />
                      <span className="truncate">{scholar.profile.position_zh || scholar.profile.position}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="h-4 w-4 mr-1 flex-shrink-0" />
                      <span className="truncate">{scholar.profile.affiliation_zh || scholar.profile.affiliation}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* 学术指标 */}
                <div className="grid grid-cols-4 gap-4 p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <p className="text-lg font-bold text-blue-600">{scholar.indices.hindex}</p>
                    <p className="text-xs text-gray-500">H指数</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-green-600">{scholar.indices.citations}</p>
                    <p className="text-xs text-gray-500">引用数</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-purple-600">{scholar.indices.pubs}</p>
                    <p className="text-xs text-gray-500">论文数</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-orange-600">{scholar.indices.gindex}</p>
                    <p className="text-xs text-gray-500">G指数</p>
                  </div>
                </div>

                {/* 活跃度和影响力指标 */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">学术活跃度</span>
                    <span className="text-sm font-medium">{scholar.indices.activity.toFixed(1)}</span>
                  </div>
                  <Progress value={Math.min(scholar.indices.activity, 100)} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">新星指数</span>
                    <span className="text-sm font-medium">{scholar.indices.newStar.toFixed(1)}</span>
                  </div>
                  <Progress value={Math.min(scholar.indices.newStar * 2, 100)} className="h-2" />
                </div>

                {/* 研究领域标签 */}
                <div>
                  <p className="text-sm font-medium mb-2">主要研究领域</p>
                  <div className="flex flex-wrap gap-1">
                    {scholar.tags.slice(0, 6).map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                        {scholar.tags_score[index] && (
                          <span className="ml-1 text-blue-600">({scholar.tags_score[index]})</span>
                        )}
                      </Badge>
                    ))}
                    {scholar.tags.length > 6 && (
                      <Badge variant="outline" className="text-xs">
                        +{scholar.tags.length - 6}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* 社交统计 */}
                <div className="flex items-center justify-between text-sm text-gray-500 pt-2 border-t">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center">
                      <Eye className="h-4 w-4 mr-1" />
                      {scholar.num_viewed}
                    </div>
                    <div className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      {scholar.num_followed}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {scholar.links?.gs && (
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                        <a href={scholar.links.gs.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    {scholar.profile.homepage && (
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                        <a href={scholar.profile.homepage} target="_blank" rel="noopener noreferrer">
                          <Globe className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    <Link href={`/research?scholar=${scholar.id}`}>
                      <Button size="sm">查看成果</Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredScholars.length === 0 && (
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">未找到匹配的学者</h3>
            <p className="text-gray-500 mb-4">请尝试调整筛选条件或搜索关键词</p>
            <Button onClick={() => setShowAddDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              新增学者
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
