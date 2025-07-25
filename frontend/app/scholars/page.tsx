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
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Plus, Filter, Download, MapPin, GraduationCap, ExternalLink, Globe, Eye, Users } from "lucide-react"
import Link from "next/link"
import type { Scholar } from "../types/api-types"
import { useSearchParams } from "next/navigation"

// 1. 定义PaperRaw和PatentRaw类型

type PaperRaw = {
  id: string;
  title?: string;
  abstract?: string;
  authors?: object[];
  year?: number;
  lang?: string;
  n_citation?: number;
  pdf?: string;
  urls?: object[];
  versions?: object[];
  create_time?: string;
  update_times?: object[];
};

type PatentRaw = {
  id: string;
  title?: object;
  abstract?: object;
  app_date?: string;
  app_num?: string;
  applicant?: object[];
  assignee?: object[];
  country?: string;
  cpc?: object[];
  inventor?: object[];
  ipc?: object[];
  ipcr?: object[];
  pct?: object[];
  priority?: object[];
  pub_date?: string;
  pub_kind?: string;
  pub_num?: string;
  pub_search_id?: string;
};

export default function ScholarsPage() {
  const searchParams = useSearchParams();
  const [scholars, setScholars] = useState<Scholar[]>([])
  const [filteredScholars, setFilteredScholars] = useState<Scholar[]>([])
  const [searchTerm] = useState("")
  const [selectedAffiliation] = useState<string>("all")
  const [selectedNation] = useState<string>("all")
  const [hIndexRange] = useState<[number, number]>([0, 100])
  const [citationRange] = useState<[number, number]>([0, 10000])
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [addScholarName, setAddScholarName] = useState("")
  const [searching, setSearching] = useState(false)
  const [searchResult, setSearchResult] = useState<Scholar[]>([])
  const [selectedScholar, setSelectedScholar] = useState<Scholar | null>(null)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(9)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  // 展开研究领域标签的学者id集合
  const [expandedTags, setExpandedTags] = useState<Record<string, boolean>>({});
  const toggleTags = (id: string) => {
    setExpandedTags((prev) => ({ ...prev, [id]: !prev[id] }));
  };
  const [showFetchDialog, setShowFetchDialog] = useState(false)
  const [fetching, setFetching] = useState(false)
  const [fetchDone, setFetchDone] = useState(false)
  const [fetchStep, setFetchStep] = useState<string>("")
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [refreshFlag, setRefreshFlag] = useState(0); // 新增：用于强制刷新学者列表
  const [featureDialogOpen, setFeatureDialogOpen] = useState(false)
  const [filterDialogOpen, setFilterDialogOpen] = useState(false)

  // 分页获取真实后端数据
  useEffect(() => {
    const fetchScholars = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/scholars/list?size=${pageSize}&offset=${(page-1)*pageSize}`, {
          headers: {
            Authorization: `Basic ${btoa('admin:admin')}`
          }
        })
        if (!res.ok) throw new Error('请求失败')
        const data = await res.json()
        setScholars(data.data)
        setTotal(data.total)
      } catch {
        setScholars([])
        setTotal(0)
      } finally {
        setLoading(false)
      }
    }
    fetchScholars()
  }, [page, pageSize, refreshFlag]) // 新增refreshFlag依赖

  // 筛选逻辑
  useEffect(() => {
    const filtered = scholars.filter((scholar) => {
      const matchesSearch =
        !searchTerm ||
        scholar.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (scholar.name_zh && scholar.name_zh.includes(searchTerm)) ||
        (scholar.profile?.affiliation?.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (scholar.profile?.affiliation_zh && scholar.profile.affiliation_zh.includes(searchTerm))
      return matchesSearch
    })
    setFilteredScholars(filtered)
  }, [scholars, searchTerm, selectedAffiliation, selectedNation, hIndexRange, citationRange])

  useEffect(() => {
    if (searchParams.get("action") === "add") {
      setShowAddDialog(true);
    }
  }, [searchParams]);

  const exportData = () => {
    setFeatureDialogOpen(true)
  }

  // 新增学者弹窗内搜索逻辑
  const handleSearchScholar = async () => {
    if (!addScholarName.trim()) return;
    setSearching(true)
    setSearchError(null)
    setSelectedScholar(null)
    try {
      const res = await fetch(`/api/scholars?name=${encodeURIComponent(addScholarName)}`)
      if (!res.ok) throw new Error('搜索失败')
      const data = await res.json()
      if (!data.data || data.data.length === 0) {
        setSearchResult([])
        setSearchError('未找到相关学者')
      } else {
        setSearchResult(data.data)
      }
    } catch {
      setSearchResult([])
      setSearchError('搜索出错')
    } finally {
      setSearching(false)
    }
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
              <h1 className="text-xl font-semibold text-gray-900">学者检索</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Button onClick={exportData} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                导出数据
              </Button>
              <Dialog open={featureDialogOpen} onOpenChange={setFeatureDialogOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>提示</DialogTitle>
                    <DialogDescription>该功能暂未开放，敬请期待！</DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
              <Dialog open={showAddDialog} onOpenChange={(open) => {
                setShowAddDialog(open);
                if (!open) {
                  setAddScholarName("");
                  setSearchResult([]);
                  setSelectedScholar(null);
                  setSearchError(null);
                  setShowFetchDialog(false);
                  setFetching(false);
                  setFetchDone(false);
                  setFetchStep("");
                  setFetchError(null);
                  setRefreshFlag(f => f + 1); // 关闭弹窗时刷新学者列表
                }
              }}>
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
                      disabled={searching}
                    />
                    <Button className="w-full" onClick={handleSearchScholar} disabled={searching || !addScholarName.trim()}>
                      {searching ? '搜索中...' : '搜索学者'}
                    </Button>
                    {searchError && <div className="text-red-500 text-sm">{searchError}</div>}
                    {searchResult.length > 0 && (
                      <div className="max-h-60 overflow-y-auto border rounded p-2 space-y-2">
                        {searchResult.map((scholar: Scholar) => {
                          return (
                            <div
                              key={scholar.id}
                              className={`flex flex-col items-start p-2 rounded cursor-pointer border transition-colors ${selectedScholar?.id === scholar.id ? 'border-blue-500 bg-blue-50' : 'border-transparent hover:bg-gray-100'}`}
                              style={{ maxHeight: '70px', overflow: 'hidden' }}
                              onClick={() => setSelectedScholar(scholar)}
                            >
                              <div className="flex items-center w-full mb-1">
                                <Avatar className="w-8 h-8 mr-2">
                                  <AvatarImage src={scholar.avatar || "/placeholder.svg"} alt={scholar.name} />
                                  <AvatarFallback>{scholar.name_zh ? scholar.name_zh.charAt(0) : scholar.name.charAt(0)}</AvatarFallback>
                                </Avatar>
                                <div className="flex-1 min-w-0">
                                  <div className="font-medium text-base leading-tight">{scholar.name_zh || scholar.name}</div>
                                  <div className="text-xs text-gray-500 truncate max-w-[250px]" 
                                   title={typeof (scholar as { org_zh?: string; org?: string }).org_zh === 'string' ? (scholar as { org_zh?: string }).org_zh : (typeof (scholar as { org?: string }).org === 'string' ? (scholar as { org?: string }).org : "")}
                                  >
                                   {typeof (scholar as { org_zh?: string; org?: string }).org_zh === 'string' ? (scholar as { org_zh?: string }).org_zh : (typeof (scholar as { org?: string }).org === 'string' ? (scholar as { org?: string }).org : "")}
                                  </div>
                                </div>
                                {selectedScholar?.id === scholar.id && <span className="ml-2 text-blue-600 text-xs">已选中</span>}
                              </div>
                              <div className="w-full flex flex-row flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600">
                                <div>引用数：{typeof (scholar as { n_citation?: number }).n_citation === 'number' ? (scholar as { n_citation?: number }).n_citation : '--'}</div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                    {selectedScholar && (
                      <>
                        <div className="mt-2 p-2 border rounded bg-blue-50 text-blue-700 text-sm">
                          已选择学者：{selectedScholar.name_zh || selectedScholar.name}
                        </div>
                        <Button
                          className="w-full mt-2"
                          variant="default"
                          onClick={() => setShowFetchDialog(true)}
                        >
                          确认拉取
                        </Button>
                        <Dialog open={showFetchDialog} onOpenChange={open => { setShowFetchDialog(open); if (!open) { setFetching(false); setFetchDone(false); } }}>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>确认拉取学者数据</DialogTitle>
                              <DialogDescription>
                                即将拉取学者 {selectedScholar.name_zh || selectedScholar.name} 的所有论文和专利，是否继续？
                              </DialogDescription>
                            </DialogHeader>
                            {fetching || fetchStep ? (
                              <div className="text-blue-600 py-2">{fetchStep}</div>
                            ) : fetchDone ? (
                              <div className="text-green-600 py-4">拉取完成！</div>
                            ) : null}
                            {fetchError && <div className="text-red-600 py-2">{fetchError}</div>}
                            <DialogFooter>
                              {fetchDone ? (
                                <Button
                                  variant="default"
                                  onClick={() => {
                                    setShowFetchDialog(false);
                                    setShowAddDialog(false);
                                    setRefreshFlag(f => f + 1); // 返回时刷新学者列表
                                  }}
                                >返回</Button>
                              ) : (
                                <>
                                  <DialogClose asChild>
                                    <Button variant="outline" disabled={fetching}>取消</Button>
                                  </DialogClose>
                                  <Button
                                    onClick={async () => {
                                      if (!selectedScholar) return;
                                      setFetching(true)
                                      setFetchStep("拉取学者详细信息...")
                                      setFetchError(null)
                                      try {
                                        // 1. 拉取AMiner学者详细信息
                                        const scholarDetailRes = await fetch(`/api/scholars/aminer/${selectedScholar.id}/detail`, {
                                          headers: { Authorization: `Basic ${btoa('admin:admin')}` }
                                        })
                                        if (!scholarDetailRes.ok) throw new Error('学者详情拉取失败')
                                        const scholarDetail = await scholarDetailRes.json()
                                        setFetchStep("保存学者到本地...")
                                        // 2. 持久化学者
                                        const scholarSaveRes = await fetch('/api/scholars', {
                                          method: 'POST',
                                          headers: { 'Content-Type': 'application/json', Authorization: `Basic ${btoa('admin:admin')}` },
                                          body: JSON.stringify(scholarDetail)
                                        })
                                        if (!scholarSaveRes.ok) throw new Error('学者保存失败')
                                        const scholarSaved = await scholarSaveRes.json()
                                        const localScholarId = scholarSaved.id
                                        setFetchStep("拉取论文...")
                                        // 3. 拉取论文
                                        const papersRes = await fetch(`/api/scholars/${selectedScholar.id}/papers?size=1000`, {
                                          headers: { Authorization: `Basic ${btoa('admin:admin')}` }
                                        })
                                        if (!papersRes.ok) throw new Error('论文拉取失败')
                                        const papersData = await papersRes.json()
                                        const papers: PaperRaw[] = papersData.hitList || papersData || []
                                        setFetchStep(`保存论文（共${papers.length}篇）...`)
                                        // 4. 持久化论文
                                        if (papers.length > 0) {
                                          const paperBodies = papers.map((p: PaperRaw) => ({
                                            aminer_id: p.id,
                                            scholar_id: localScholarId,
                                            title: p.title || '',
                                            abstract: p.abstract || '',
                                            authors: JSON.stringify(p.authors || []),
                                            year: p.year || 0,
                                            lang: p.lang || '',
                                            num_citation: p.n_citation || 0,
                                            pdf: p.pdf || '',
                                            urls: JSON.stringify(p.urls || []),
                                            versions: JSON.stringify(p.versions || []),
                                            create_time: p.create_time || '',
                                            update_times: JSON.stringify(p.update_times || [])
                                          }))
                                          setFetchStep(`批量保存论文（共${paperBodies.length}篇）...`)
                                          const res = await fetch('/api/papers/batch', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json', Authorization: `Basic ${btoa('admin:admin')}` },
                                            body: JSON.stringify(paperBodies)
                                          })
                                          if (!res.ok) throw new Error('论文批量保存失败')
                                        }
                                        setFetchStep("拉取专利...")
                                        // 5. 拉取专利
                                        const patentsRes = await fetch(`/api/scholars/${selectedScholar.id}/patents?size=1000`, {
                                          headers: { Authorization: `Basic ${btoa('admin:admin')}` }
                                        })
                                        if (!patentsRes.ok) throw new Error('专利拉取失败')
                                        const patentsData = await patentsRes.json()
                                        const patents: PatentRaw[] = patentsData.hitList || patentsData || []
                                        setFetchStep(`保存专利（共${patents.length}项）...`)
                                        // 6. 持久化专利
                                        if (patents.length > 0) {
                                          const patentBodies = patents.map((pt: PatentRaw) => ({
                                            aminer_id: pt.id,
                                            scholar_id: localScholarId,
                                            title: JSON.stringify(pt.title || {}),
                                            abstract: JSON.stringify(pt.abstract || {}),
                                            app_date: pt.app_date || '',
                                            app_num: pt.app_num || '',
                                            applicant: JSON.stringify(pt.applicant || []),
                                            assignee: JSON.stringify(pt.assignee || []),
                                            country: pt.country || '',
                                            cpc: JSON.stringify(pt.cpc || []),
                                            inventor: JSON.stringify(pt.inventor || []),
                                            ipc: JSON.stringify(pt.ipc || []),
                                            ipcr: JSON.stringify(pt.ipcr || []),
                                            pct: JSON.stringify(pt.pct || []),
                                            priority: JSON.stringify(pt.priority || []),
                                            pub_date: pt.pub_date || '',
                                            pub_kind: pt.pub_kind || '',
                                            pub_num: pt.pub_num || '',
                                            pub_search_id: pt.pub_search_id || ''
                                          }))
                                          setFetchStep(`批量保存专利（共${patentBodies.length}项）...`)
                                          const res = await fetch('/api/patents/batch', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json', Authorization: `Basic ${btoa('admin:admin')}` },
                                            body: JSON.stringify(patentBodies)
                                          })
                                          if (!res.ok) throw new Error('专利批量保存失败')
                                        }
                                        setFetchStep("全部完成！")
                                        setFetching(false)
                                        setFetchDone(true)
                                      } catch (e: unknown) {
                                        if (e instanceof Error) {
                                          setFetchError(e.message || '拉取失败')
                                        } else {
                                          setFetchError('拉取失败')
                                        }
                                        setFetching(false)
                                      }
                                    }}
                                    disabled={fetching || fetchDone || !selectedScholar}
                                  >
                                    {fetching ? '拉取中...' : '确认'}
                                  </Button>
                                </>
                              )}
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </>
                    )}
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 筛选区域禁用，点击弹窗提示 */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Filter className="h-5 w-5 mr-2" />
              筛选条件
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div onClick={() => setFilterDialogOpen(true)} style={{ cursor: 'not-allowed' }}>
                <label className="text-sm font-medium mb-2 block">搜索</label>
                <Input placeholder="姓名、机构、研究方向..." value={""} disabled />
              </div>
              <div onClick={() => setFilterDialogOpen(true)} style={{ cursor: 'not-allowed' }}>
                <label className="text-sm font-medium mb-2 block">国家/地区</label>
                <Select value={"all"} disabled>
                  <SelectTrigger>
                    <SelectValue placeholder="选择国家/地区" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">全部国家</SelectItem>
                    <SelectItem value="CN">中国</SelectItem>
                    <SelectItem value="US">美国</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div onClick={() => setFilterDialogOpen(true)} style={{ cursor: 'not-allowed' }}>
                <label className="text-sm font-medium mb-2 block">标签</label>
                <Input placeholder="输入标签" value={""} disabled />
              </div>
            </div>
            <Dialog open={filterDialogOpen} onOpenChange={setFilterDialogOpen}>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>提示</DialogTitle>
                  <DialogDescription>筛选功能暂未开放，敬请期待！</DialogDescription>
                </DialogHeader>
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>

        {/* 结果统计 */}
        <div className="flex justify-between items-center mb-6">
          <p className="text-sm text-gray-600">
            共找到 <span className="font-semibold">{filteredScholars.length}</span> 位学者
          </p>
        </div>

        {/* 学者卡片网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-stretch">
          {filteredScholars.map((scholar) => (
            <Card key={scholar.id} className="w-full h-full hover:shadow-lg transition-shadow max-w-md mx-auto gap-2">
              <CardHeader className="pb-4">
                <div className="flex items-start space-x-4 min-w-0">
                  <Avatar className="w-16 h-16">
                    <AvatarImage src={scholar.avatar || "/placeholder.svg"} alt={scholar.name} className="object-cover" />
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
                      <span className="truncate block" title={scholar.profile?.position_zh || scholar.profile?.position || ''}>{scholar.profile?.position_zh || scholar.profile?.position || ''}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="h-4 w-4 mr-1 flex-shrink-0" />
                      <span className="truncate block" title={scholar.profile?.affiliation_zh || scholar.profile?.affiliation || ''}>{scholar.profile?.affiliation_zh || scholar.profile?.affiliation || ''}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4 w-full flex flex-col h-full">
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
                    <span className="text-sm font-medium">
                      {typeof scholar.indices.activity === 'number' ? scholar.indices.activity.toFixed(1) : '--'}
                    </span>
                  </div>
                  <Progress value={typeof scholar.indices.activity === 'number' ? Math.min(scholar.indices.activity, 100) : 0} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">新星指数</span>
                    <span className="text-sm font-medium">
                      {typeof scholar.indices.newStar === 'number' ? scholar.indices.newStar.toFixed(1) : '--'}
                    </span>
                  </div>
                  <Progress value={typeof scholar.indices.newStar === 'number' ? Math.min(scholar.indices.newStar * 2, 100) : 0} className="h-2" />
                </div>

                {/* 研究领域标签 */}
                <div>
                  <p className="text-sm font-medium mb-2">主要研究领域</p>
                  <div className="flex flex-wrap gap-1 w-full min-h-[32px]">
                    {(expandedTags[scholar.id] ? scholar.tags : scholar.tags.slice(0, 6)).map((tag: string, index: number) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {tag}
                        {scholar.tags_score[index] && (
                          <span className="ml-1 text-blue-600">({scholar.tags_score[index]})</span>
                        )}
                      </Badge>
                    ))}
                    {scholar.tags.length > 6 && !expandedTags[scholar.id] && (
                      <Badge variant="outline" className="text-xs cursor-pointer" onClick={() => toggleTags(scholar.id)}>
                        +{scholar.tags.length - 6}
                      </Badge>
                    )}
                    {scholar.tags.length > 6 && expandedTags[scholar.id] && (
                      <Badge variant="outline" className="text-xs cursor-pointer" onClick={() => toggleTags(scholar.id)}>
                        收起
                      </Badge>
                    )}
                  </div>
                </div>

                {/* 社交统计 */}
                <div className="flex items-center justify-between text-sm text-gray-500 pt-2 border-t mt-auto">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center" title="被浏览次数">
                      <Eye className="h-4 w-4 mr-1" />
                      {scholar.num_viewed}
                    </div>
                    <div className="flex items-center" title="被关注人数">
                      <Users className="h-4 w-4 mr-1" />
                      {scholar.num_followed}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {scholar.links?.gs && scholar.links.gs.url && (
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild title="谷歌学术">
                        <a href={scholar.links.gs.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    {scholar.profile.homepage && (
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild title="个人主页">
                        <a href={scholar.profile.homepage} target="_blank" rel="noopener noreferrer">
                          <Globe className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    <Link href={`/research?scholarId=${scholar.id}`}>
                      <Button size="sm" className="cursor-pointer">查看成果</Button>
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
        {filteredScholars.length > 0 && (
          <div className="flex justify-center mt-8">
            <div className="inline-flex items-center space-x-2">
              <Button
                onClick={() => setPage(page-1)}
                disabled={page===1 || loading}
                variant="outline"
                size="sm"
                className="cursor-pointer"
              >
                上一页
              </Button>
              {Array.from({ length: Math.ceil(total/pageSize) }, (_, i) => i + 1).map((num) => (
                <Button
                  key={num}
                  onClick={() => setPage(num)}
                  variant={num === page ? 'default' : 'outline'}
                  size="sm"
                  className="cursor-pointer"
                  disabled={loading}
                >
                  {num}
                </Button>
              ))}
              <Button
                onClick={() => setPage(page+1)}
                disabled={page*pageSize>=total || loading}
                variant="outline"
                size="sm"
                className="cursor-pointer"
              >
                下一页
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
