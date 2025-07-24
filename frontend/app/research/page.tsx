"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Search,
  Filter,
  Download,
  Plus,
  Edit,
  Trash2,
  FileText,
  Award,
  Calendar,
  Users,
  ExternalLink,
  Brain,
  Quote,
  Globe,
  Building,
  Hash,
  Clock,
  CheckCircle,
} from "lucide-react"
import Link from "next/link"
import type { Paper, Patent } from "../types/api-types"

export default function ResearchPage() {
  const [activeTab, setActiveTab] = useState("papers")
  const [papers, setPapers] = useState<Paper[]>([])
  const [patents, setPatents] = useState<Patent[]>([])
  const [totalPapers, setTotalPapers] = useState(0)
  const [totalPatents, setTotalPatents] = useState(0)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedYear, setSelectedYear] = useState<string>("all")
  const [selectedAuthor, setSelectedAuthor] = useState<string>("all")
  const [selectedSource, setSelectedSource] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [selectedCountry, setSelectedCountry] = useState<string>("all")
  const [citationRange, setCitationRange] = useState<[number, number]>([0, 1000])
  const [authorHoverId, setAuthorHoverId] = useState<string | null>(null)
  const [featureDialogOpen, setFeatureDialogOpen] = useState(false)
  // 分页
  const [paperPage, setPaperPage] = useState(1)
  const [paperPageSize, setPaperPageSize] = useState(10)
  const [patentPage, setPatentPage] = useState(1)
  const [patentPageSize, setPatentPageSize] = useState(10)

  // 拉取论文和专利数据（根据筛选和分页）
  useEffect(() => {
    async function fetchPapers() {
      try {
        const params = new URLSearchParams()
        params.append("size", String(paperPageSize))
        params.append("offset", String((paperPage - 1) * paperPageSize))
        if (searchTerm) params.append("author", searchTerm) // 可扩展为title/abstract等
        if (selectedYear !== "all") params.append("year", selectedYear)
        // 这里可以扩展更多筛选条件，如 selectedAuthor, selectedSource, citationRange
        const res = await fetch(`/api/papers/list?${params.toString()}`, { credentials: "include" })
        if (!res.ok) throw new Error("论文数据获取失败")
        const data = await res.json()
        setPapers(Array.isArray(data.data) ? data.data : [])
        setTotalPapers(data.total || 0)
      } catch (e) {
        setPapers([])
        setTotalPapers(0)
      }
    }
    if (activeTab === "papers") fetchPapers()
    // eslint-disable-next-line
  }, [activeTab, searchTerm, selectedYear, paperPage, paperPageSize])

  useEffect(() => {
    async function fetchPatents() {
      try {
        const params = new URLSearchParams()
        params.append("size", String(patentPageSize))
        params.append("offset", String((patentPage - 1) * patentPageSize))
        if (searchTerm) params.append("inventor", searchTerm)
        if (selectedCountry !== "all") params.append("country", selectedCountry)
        if (selectedStatus !== "all") params.append("pub_status", selectedStatus)
        const res = await fetch(`/api/patents/list?${params.toString()}`, { credentials: "include" })
        if (!res.ok) throw new Error("专利数据获取失败")
        const data = await res.json()
        setPatents(Array.isArray(data.data) ? data.data : [])
        setTotalPatents(data.total || 0)
      } catch (e) {
        setPatents([])
        setTotalPatents(0)
      }
    }
    if (activeTab === "patents") fetchPatents()
    // eslint-disable-next-line
  }, [activeTab, searchTerm, selectedCountry, selectedStatus, patentPage, patentPageSize])

  // 筛选逻辑
  useEffect(() => {
    if (activeTab === "papers") {
      const filtered = papers.filter((paper) => {
        const matchesSearch =
          paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          paper.authors.some((author) => author.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
          paper.abstract.toLowerCase().includes(searchTerm.toLowerCase())

        const matchesYear = selectedYear === "all" || paper.year.toString() === selectedYear
        const matchesAuthor = selectedAuthor === "all" || paper.authors.some((author) => author.name === selectedAuthor)
        const matchesSource =
          selectedSource === "all" ||
          (paper.versions && paper.versions.some((version) => version.src === selectedSource))
        const matchesCitations = paper.num_citation >= citationRange[0] && paper.num_citation <= citationRange[1]

        return matchesSearch && matchesYear && matchesAuthor && matchesSource && matchesCitations
      })
      // setFilteredPapers(filtered) // This line is removed as per the new_code
    } else {
      const filtered = patents.filter((patent) => {
        const titleText = patent.title.zh?.[0] || patent.title.en?.[0] || ""
        const abstractText = patent.abstract.zh?.[0] || patent.abstract.en?.[0] || ""

        const matchesSearch =
          titleText.toLowerCase().includes(searchTerm.toLowerCase()) ||
          patent.inventor.some((inventor) => inventor.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
          abstractText.toLowerCase().includes(searchTerm.toLowerCase())

        const matchesCountry = selectedCountry === "all" || patent.country === selectedCountry

        // 根据发布状态判断专利状态
        const patentStatus = patent.pubDate ? "published" : "pending"
        const matchesStatus = selectedStatus === "all" || patentStatus === selectedStatus

        return matchesSearch && matchesCountry && matchesStatus
      })
      // setFilteredPatents(filtered) // This line is removed as per the new_code
    }
  }, [
    papers,
    patents,
    searchTerm,
    selectedYear,
    selectedAuthor,
    selectedSource,
    selectedStatus,
    selectedCountry,
    citationRange,
    activeTab,
  ])

  const exportData = () => {
    console.log("Exporting research data...")
  }

  const handleEdit = (item: Paper | Patent) => {
    console.log("Editing item:", item.id)
  }

  const handleDelete = (id: string) => {
    if (activeTab === "papers") {
      setPapers(papers.filter((p) => p.id !== id))
    } else {
      setPatents(patents.filter((p) => p.id !== id))
    }
  }

  const uniqueYears = Array.from(new Set(papers.map((p) => p.year.toString())))
    .sort()
    .reverse()
  const uniqueAuthors = Array.from(new Set(papers.flatMap((p) => p.authors.map((a) => a.name))))
  const uniqueSources = Array.from(new Set(papers.flatMap((p) => p.versions?.map((v) => v.src) || []))).filter(Boolean)

  const getPatentStatusIcon = (patent: Patent) => {
    if (patent.pubDate) {
      return <CheckCircle className="h-4 w-4 text-green-600" />
    }
    return <Clock className="h-4 w-4 text-yellow-600" />
  }

  const getPatentStatusText = (patent: Patent) => {
    return patent.pubDate ? "已公开" : "申请中"
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("zh-CN")
  }

  // 分页控件
  function Pagination({ page, pageSize, total, onPageChange, onPageSizeChange }: { page: number, pageSize: number, total: number, onPageChange: (p: number) => void, onPageSizeChange: (s: number) => void }) {
    const totalPages = Math.ceil(total / pageSize)
    return (
      <div className="flex items-center justify-between mt-4">
        <div>
          <span>共 {total} 条，{page}/{totalPages} 页</span>
        </div>
        <div className="flex items-center space-x-2">
          <Button size="sm" variant="outline" disabled={page === 1} onClick={() => onPageChange(page - 1)}>上一页</Button>
          <span>{page}</span>
          <Button size="sm" variant="outline" disabled={page === totalPages || totalPages === 0} onClick={() => onPageChange(page + 1)}>下一页</Button>
          <select value={pageSize} onChange={e => onPageSizeChange(Number(e.target.value))} className="ml-2 border rounded px-2 py-1 text-sm">
            {[10, 20, 50].map(s => <option key={s} value={s}>{s}条/页</option>)}
          </select>
        </div>
      </div>
    )
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
              <h1 className="text-xl font-semibold text-gray-900">论文专利检索</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Button onClick={exportData} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                导出数据
              </Button>
              <Dialog>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    批量拉取
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>批量拉取数据</DialogTitle>
                    <DialogDescription>通过AMiner API批量拉取学者的论文和专利数据</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">学者ID</label>
                      <Input placeholder="输入AMiner学者ID" />
                    </div>
                    <div>
                      <label className="text-sm font-medium mb-2 block">时间范围</label>
                      <div className="flex space-x-2">
                        <Input type="date" />
                        <Input type="date" />
                      </div>
                    </div>
                    <Button className="w-full">开始拉取</Button>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">搜索</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="标题、作者、摘要..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {activeTab === "papers" ? (
                <>
                  <div>
                    <label className="text-sm font-medium mb-2 block">年份</label>
                    <Select value={selectedYear} onValueChange={setSelectedYear}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择年份" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部年份</SelectItem>
                        {uniqueYears.map((year) => (
                          <SelectItem key={year} value={year}>
                            {year}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">作者</label>
                    <Select value={selectedAuthor} onValueChange={setSelectedAuthor}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择作者" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部作者</SelectItem>
                        {uniqueAuthors.slice(0, 20).map((author) => (
                          <SelectItem key={author} value={author}>
                            {author}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">数据源</label>
                    <Select value={selectedSource} onValueChange={setSelectedSource}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择数据源" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部数据源</SelectItem>
                        {uniqueSources.map((source) => (
                          <SelectItem key={source} value={source}>
                            {source}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="text-sm font-medium mb-2 block">国家/地区</label>
                    <Select value={selectedCountry} onValueChange={setSelectedCountry}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择国家" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部国家</SelectItem>
                        <SelectItem value="CN">中国</SelectItem>
                        <SelectItem value="US">美国</SelectItem>
                        <SelectItem value="JP">日本</SelectItem>
                        <SelectItem value="KR">韩国</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">状态</label>
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择状态" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部状态</SelectItem>
                        <SelectItem value="pending">申请中</SelectItem>
                        <SelectItem value="published">已公开</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}
            </div>

            {activeTab === "papers" && false && (
              <div className="mt-4">
                <label className="text-sm font-medium mb-2 block">引用数范围</label>
                <div className="flex items-center space-x-2">
                  <Input
                    type="number"
                    placeholder="最小值"
                    value={citationRange[0]}
                    onChange={(e) => setCitationRange([Number.parseInt(e.target.value) || 0, citationRange[1]])}
                    className="w-24"
                  />
                  <span>-</span>
                  <Input
                    type="number"
                    placeholder="最大值"
                    value={citationRange[1]}
                    onChange={(e) => setCitationRange([citationRange[0], Number.parseInt(e.target.value) || 1000])}
                    className="w-24"
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 主要内容区域 */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex justify-between items-center mb-6">
            <TabsList>
              <TabsTrigger value="papers" className="flex items-center">
                <FileText className="h-4 w-4 mr-2" />
                论文 ({totalPapers})
              </TabsTrigger>
              <TabsTrigger value="patents" className="flex items-center">
                <Award className="h-4 w-4 mr-2" />
                专利 ({totalPatents})
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="papers">
            <div className="space-y-6">
              {papers.map((paper) => (
                <Card key={paper.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-3 leading-tight">{paper.title}</CardTitle>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center" style={{ position: 'relative' }}>
                            <Users className="h-4 w-4 mr-1" />
                            <span
                              className="truncate max-w-md"
                              style={{ display: 'inline-block' }}
                              onMouseEnter={() => setAuthorHoverId(paper.id)}
                              onMouseLeave={() => setAuthorHoverId(null)}
                            >
                              {paper.authors.map((author) => author.name).join(", ")}
                              {authorHoverId === paper.id && (
                                <span
                                  className="absolute left-0 top-full mt-1 bg-white shadow-lg rounded px-2 py-1 z-10 text-gray-900 whitespace-pre-wrap min-w-full"
                                  style={{ minWidth: 'max-content', whiteSpace: 'pre-line' }}
                                >
                                  {paper.authors.map((author) => author.name).join(", ")}
                                </span>
                              )}
                            </span>
                          </div>
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {paper.year}
                          </div>
                          <div className="flex items-center">
                            <Quote className="h-4 w-4 mr-1" />
                            {paper.num_citation} 引用
                          </div>
                          <div className="flex items-center">
                            <Globe className="h-4 w-4 mr-1" />
                            {paper.lang.toUpperCase()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700" onClick={() => setFeatureDialogOpen(true)}>
                          <Brain className="h-4 w-4 mr-1" />
                          AI分析
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setFeatureDialogOpen(true)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setFeatureDialogOpen(true)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* 数据源版本 */}
                      {paper.versions && paper.versions.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {paper.versions.map((version, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {version.src}
                              {version.sid && <span className="ml-1">({version.sid})</span>}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* 摘要 */}
                      <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">{paper.abstract}</p>

                      {/* 操作按钮 */}
                      <div className="flex items-center justify-between pt-2 border-t">
                        <div className="flex items-center space-x-2 text-xs text-gray-500">
                          <span>创建: {formatDate(paper.create_time)}</span>
                          <span>•</span>
                          <span>更新: {formatDate(paper.update_times.u_a_t)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          {paper.pdf && (
                            <Button variant="outline" size="sm" asChild>
                              <a href={paper.pdf} target="_blank" rel="noopener noreferrer">
                                <FileText className="h-4 w-4 mr-1" />
                                PDF
                              </a>
                            </Button>
                          )}
                          {paper.urls && paper.urls[0] && (
                            <Button variant="outline" size="sm" asChild>
                              <a href={paper.urls[0]} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-4 w-4 mr-1" />
                                原文
                              </a>
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Pagination page={paperPage} pageSize={paperPageSize} total={totalPapers} onPageChange={setPaperPage} onPageSizeChange={s => { setPaperPageSize(s); setPaperPage(1) }} />
          </TabsContent>

          <TabsContent value="patents">
            <div className="space-y-6">
              {patents.map((patent) => (
                <Card key={patent.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className="text-lg mb-3 leading-tight">
                          {patent.title.zh?.[0] || patent.title.en?.[0]}
                        </CardTitle>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center">
                            <Users className="h-4 w-4 mr-1" />
                            <span className="truncate max-w-md">
                              {patent.inventor.map((inv) => inv.name).join(", ")}
                            </span>
                          </div>
                          <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            申请: {formatDate(patent.appDate)}
                          </div>
                          {patent.pubDate && (
                            <div className="flex items-center">
                              <Calendar className="h-4 w-4 mr-1" />
                              公开: {formatDate(patent.pubDate)}
                            </div>
                          )}
                          <div className="flex items-center">
                            <Globe className="h-4 w-4 mr-1" />
                            {patent.country}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <div className="flex items-center">
                          {getPatentStatusIcon(patent)}
                          <span className="ml-1 text-sm">{getPatentStatusText(patent)}</span>
                        </div>
                        <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
                          <Brain className="h-4 w-4 mr-1" />
                          AI分析
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(patent)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(patent.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* 专利号和申请信息 */}
                      <div className="flex flex-wrap gap-4 text-sm">
                        {patent.appNum && (
                          <div className="flex items-center">
                            <Hash className="h-4 w-4 mr-1 text-gray-400" />
                            <span className="font-mono">申请号: {patent.appNum}</span>
                          </div>
                        )}
                        {patent.pubNum && (
                          <div className="flex items-center">
                            <Hash className="h-4 w-4 mr-1 text-gray-400" />
                            <span className="font-mono">公开号: {patent.pubNum}</span>
                          </div>
                        )}
                        {patent.pubSearchId && (
                          <div className="flex items-center">
                            <Hash className="h-4 w-4 mr-1 text-gray-400" />
                            <span className="font-mono">{patent.pubSearchId}</span>
                          </div>
                        )}
                      </div>

                      {/* 申请人信息 */}
                      <div className="flex items-center text-sm text-gray-600">
                        <Building className="h-4 w-4 mr-1" />
                        <span>申请人: {patent.applicant.map((app) => app.name).join(", ")}</span>
                      </div>

                      {/* IPC分类 */}
                      {patent.ipc && patent.ipc.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {patent.ipc.map((ipc, index) => (
                            <Badge key={index} variant="secondary" className="text-xs font-mono">
                              {ipc.l4}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* 摘要 */}
                      <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">
                        {patent.abstract.zh?.[0] || patent.abstract.en?.[0]}
                      </p>

                      {/* 优先权信息 */}
                      {patent.priority && patent.priority.length > 0 && (
                        <div className="text-xs text-gray-500">
                          优先权: {patent.priority.map((p) => p.num).join(", ")}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Pagination page={patentPage} pageSize={patentPageSize} total={totalPatents} onPageChange={setPatentPage} onPageSizeChange={s => { setPatentPageSize(s); setPatentPage(1) }} />
          </TabsContent>
        </Tabs>

        {/* 空状态 */}
        {((activeTab === "papers" && papers.length === 0) ||
          (activeTab === "patents" && patents.length === 0)) && (
          <div className="text-center py-12">
            {activeTab === "papers" ? (
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            ) : (
              <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            )}
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              未找到匹配的{activeTab === "papers" ? "论文" : "专利"}
            </h3>
            <p className="text-gray-500 mb-4">请尝试调整筛选条件或搜索关键词</p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              批量拉取数据
            </Button>
          </div>
        )}
      </div>
      <Dialog open={featureDialogOpen} onOpenChange={setFeatureDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>提示</DialogTitle>
            <DialogDescription>该功能暂未开放，敬请期待！</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  )
}
