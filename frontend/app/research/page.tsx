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
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { useSearchParams } from "next/navigation"
import type { Paper, Patent, Scholar } from "../types/api-types"
import React from "react"

export default function ResearchPage() {
  const searchParams = useSearchParams();
  const scholarId = searchParams.get("scholarId");
  const [scholar, setScholar] = useState<Scholar | null>(null);
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
  const [showCountMismatchDialog, setShowCountMismatchDialog] = useState(false)
  const [countMismatchMsg, setCountMismatchMsg] = useState("")

  // 拉取学者信息
  useEffect(() => {
    if (!scholarId) {
      setScholar(null);
      return;
    }
    async function fetchScholar() {
      try {
        const res = await fetch(`/api/scholars/${scholarId}`, {
          headers: { Authorization: `Basic ${btoa('admin:admin')}` }
        });
        if (!res.ok) throw new Error("学者信息获取失败");
        const data = await res.json();
        setScholar(data);
      } catch {
        setScholar(null);
      }
    }
    fetchScholar();
  }, [scholarId]);

  // 拉取论文和专利数据（根据scholarId筛选）
  useEffect(() => {
    async function fetchPapers() {
      try {
        const params = new URLSearchParams();
        params.append("size", String(paperPageSize));
        params.append("offset", String((paperPage - 1) * paperPageSize));
        if (scholarId) params.append("scholar_id", scholarId);
        if (searchTerm) params.append("author", searchTerm);
        if (selectedYear !== "all") params.append("year", selectedYear);
        const res = await fetch(`/api/papers/list?${params.toString()}`, { credentials: "include" });
        if (!res.ok) throw new Error("论文数据获取失败");
        const data = await res.json();
        const safeParse = (val: unknown) => {
          if (typeof val === "string") {
            try { return JSON.parse(val) } catch { return val }
          }
          return val
        }
        const papersArr = Array.isArray(data.data)
          ? data.data.map((paper: Paper) => ({
              ...paper,
              authors: safeParse(paper.authors),
              versions: safeParse(paper.versions),
              update_times: safeParse(paper.update_times),
              urls: safeParse(paper.urls)
            }))
          : [];
        setPapers(papersArr);
        setTotalPapers(data.total || 0);
        // 判断后端实际返回数和前端渲染数是否一致
        if (Array.isArray(data.data) && (data.data.length !== papersArr.length)) {
          setCountMismatchMsg(`后端实际返回论文${data.data.length}条，实际显示${papersArr.length}条。`)
          setShowCountMismatchDialog(true)
        }
      } catch {
        setPapers([]);
        setTotalPapers(0);
      }
    }
    fetchPapers();
  }, [activeTab, searchTerm, selectedYear, paperPage, paperPageSize, scholarId]);

  useEffect(() => {
    async function fetchPatents() {
      try {
        const params = new URLSearchParams();
        params.append("size", String(patentPageSize));
        params.append("offset", String((patentPage - 1) * patentPageSize));
        if (scholarId) params.append("scholar_id", scholarId);
        if (searchTerm) params.append("inventor", searchTerm);
        if (selectedCountry !== "all") params.append("country", selectedCountry);
        if (selectedStatus !== "all") params.append("pub_status", selectedStatus);
        const res = await fetch(`/api/patents/list?${params.toString()}`, { credentials: "include" });
        if (!res.ok) throw new Error("专利数据获取失败");
        const data = await res.json();
        const safeParse = (val: unknown) => {
          if (typeof val === "string") {
            try { return JSON.parse(val) } catch { return val }
          }
          return val
        }
        const patentsArr = Array.isArray(data.data)
          ? data.data.map((patent: Patent) => ({
              ...patent,
              inventor: safeParse(patent.inventor),
              applicant: safeParse(patent.applicant),
              assignee: safeParse(patent.assignee),
              ipc: safeParse(patent.ipc),
              priority: safeParse(patent.priority),
              title: safeParse(patent.title),
              abstract: safeParse(patent.abstract)
            }))
          : [];
        setPatents(patentsArr);
        setTotalPatents(data.total || 0);
        // 判断后端实际返回数和前端渲染数是否一致
        if (Array.isArray(data.data) && (data.data.length !== patentsArr.length)) {
          setCountMismatchMsg(`后端实际返回专利${data.data.length}条，实际显示${patentsArr.length}条。`)
          setShowCountMismatchDialog(true)
        }
      } catch {
        setPatents([]);
        setTotalPatents(0);
      }
    }
    fetchPatents();
  }, [activeTab, searchTerm, selectedCountry, selectedStatus, patentPage, patentPageSize, scholarId]);

  // 筛选逻辑
  useEffect(() => {
    if (activeTab === "papers") {
      papers.filter((paper) => {
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
    } else {
      patents.filter((patent) => {
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

  const uniqueYears = Array.from(new Set(papers.map((p) => p.year.toString())))
    .sort()
    .reverse()
  const uniqueAuthors = Array.from(new Set(papers.flatMap((p) => p.authors.map((a) => a.name))))
  const uniqueSources = Array.from(new Set(papers.flatMap((p) => p.versions?.map((v) => v.src) || []))).filter(Boolean)

  // 修复formatDate函数，增加判空和格式校验
  const formatDate = (dateString: string | undefined | null) => {
    if (!dateString) return "无";
    const d = new Date(dateString);
    return isNaN(d.getTime()) ? "无" : d.toLocaleDateString("zh-CN");
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
        {/* 学者信息展示 */}
        {scholar && (
          <Card className="mb-6">
            <CardHeader className="flex flex-row items-center gap-6">
              <div>
                <Image
                  src={scholar.avatar || "/placeholder.svg"}
                  alt={scholar.name_zh || scholar.name}
                  width={80}
                  height={80}
                  className="w-20 h-20 rounded-full object-cover border"
                  unoptimized={scholar.avatar ? false : true}
                  priority
                />
              </div>
              <div className="flex-1 min-w-0">
                <CardTitle className="text-2xl font-bold">{scholar.name_zh || scholar.name}</CardTitle>
                <div className="text-gray-600 text-base mb-1">{scholar.name_zh && scholar.name}</div>
                <div className="text-gray-500 text-sm mb-1">{scholar.profile?.position_zh || scholar.profile?.position}</div>
                <div className="text-gray-500 text-sm mb-1">{scholar.profile?.affiliation_zh || scholar.profile?.affiliation}</div>
                <div className="text-gray-500 text-sm mb-1">{scholar.profile?.bio_zh || scholar.profile?.bio}</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {scholar.tags?.slice(0, 8).map((tag, idx) => (
                    <Badge key={tag + '-' + idx} variant="secondary" className="text-xs">{tag}</Badge>
                  ))}
                </div>
              </div>
            </CardHeader>
          </Card>
        )}
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
                        {uniqueYears.map((year, idx) => (
                          <SelectItem key={year + '-' + idx} value={year}>
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
                        {uniqueAuthors.slice(0, 20).map((author, idx) => (
                          <SelectItem key={author + '-' + idx} value={author}>
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
                        {uniqueSources.map((source, idx) => (
                          <SelectItem key={source + '-' + idx} value={source}>
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
                <Card key={paper.id} className="hover:shadow-md transition-shadow gap-3">
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
                          {paper.versions.map((version, idx) => (
                            <Badge key={(version.id || version.sid || version.src) + '-' + idx} variant="outline" className="text-xs">
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
                          <span>更新: {formatDate(paper.update_times?.u_v_t || paper.update_times?.u_a_t)}</span>
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
                <Card key={patent.id} className="hover:shadow-md transition-shadow gap-1">
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
                              {patent.inventor.map((inv: { name: string; personId?: string }, idx: number) => (
                                <span key={(inv.personId || inv.name) + '-' + idx}>{inv.name}{idx < patent.inventor.length - 1 ? ', ' : ''}</span>
                              ))}
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

                      {/* 申请者信息 */}
                      <div className="flex items-center text-sm text-gray-600">
                        <Building className="h-4 w-4 mr-1" />
                        <span>申请者: {patent.applicant.map((app: { name: string; orgId?: string }, idx: number) => (
                          <React.Fragment key={(app.orgId || app.name) + '-' + idx}>
                            {app.name}{idx < patent.applicant.length - 1 ? ', ' : ''}
                          </React.Fragment>
                        ))}</span>
                      </div>

                      {/* IPC分类 */}
                      {patent.ipc && patent.ipc.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {patent.ipc.map((ipc: { l4?: string; l3?: string; l2?: string; l1?: string }, idx: number) => (
                            <Badge key={(ipc.l4 || ipc.l3 || ipc.l2 || ipc.l1) + '-' + idx} variant="secondary" className="text-xs font-mono">
                              {ipc.l4}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* 摘要 */}
                      <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">
                        {patent.abstract.zh?.[0] || patent.abstract.en?.[0]}
                      </p>
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
      <Dialog open={showCountMismatchDialog} onOpenChange={setShowCountMismatchDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>数据数目不一致提示</DialogTitle>
            <DialogDescription>{countMismatchMsg}</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </div>
  )
}
