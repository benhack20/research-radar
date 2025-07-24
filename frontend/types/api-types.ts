export interface Scholar {
  id: string
  name: string
  name_zh?: string
  avatar?: string
  nation?: string
  bind: boolean
  indices: {
    activity: number
    citations: number
    diversity: number
    gindex: number
    hindex: number
    newStar: number
    pubs: number
    risingStar: number
    sociability: number
  }
  profile: {
    address?: string
    affiliation: string
    affiliation_zh?: string
    bio?: string
    bio_zh?: string
    edu?: string
    edu_zh?: string
    email?: string
    gender?: string
    homepage?: string
    phone?: string
    position: string
    position_zh?: string
    work?: string
    work_zh?: string
  }
  tags: string[]
  tags_score: number[]
  tags_zh?: string[]
  links?: {
    gs?: { type: string; url: string }
    resource?: {
      resource_link: Array<{ id: string; url: string }>
    }
  }
  num_followed: number
  num_viewed: number
  num_upvoted: number
}

export interface Paper {
  id: string
  title: string
  abstract: string
  authors: Array<{
    id?: string
    name: string
  }>
  year: number
  num_citation: number
  pdf?: string
  urls?: string[]
  lang: string
  create_time: string
  update_times: {
    u_a_t: string
    u_v_t: string
  }
  versions?: Array<{
    id: string
    sid: string
    src: string
    year: number
  }>
}

export interface Patent {
  id: string
  title: {
    en?: string[]
    zh?: string[]
  }
  abstract: {
    en?: string[]
    zh?: string[]
  }
  appDate: string
  pubDate?: string
  appNum: string
  pubNum?: string
  pubSearchId?: string
  pubKind?: string
  country: string
  inventor: Array<{
    name: string
    personId?: string
  }>
  applicant: Array<{
    name: string
    orgId?: string
    addressInfo?: {
      raw: string
    }
  }>
  assignee?: Array<{
    name: string
    orgId?: string
  }>
  ipc?: Array<{
    l1: string
    l2: string
    l3: string
    l4: string
  }>
  priority?: Array<{
    num: string
  }>
}
