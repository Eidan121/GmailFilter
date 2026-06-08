export interface Account {
  id: number
  email: string
  display_name: string | null
  is_active: boolean
  last_seen: string | null
  created_at: string
}

export interface AccountStatus {
  id: number
  email: string
  is_active: boolean
}

export interface FilterCriteria {
  from?: string
  to?: string
  subject?: string
  query?: string
  hasAttachment?: boolean
  negatedQuery?: string
  size?: number
  sizeComparison?: 'larger' | 'smaller'
}

export interface FilterAction {
  addLabelIds?: string[]
  removeLabelIds?: string[]
  archive?: boolean
  markRead?: boolean
  forward?: string
}

export interface FilterOut {
  id: string
  criteria: FilterCriteria
  action: FilterAction
}

export interface FilterCreate {
  criteria: FilterCriteria
  action: FilterAction
}

export interface LabelColor {
  textColor?: string
  backgroundColor?: string
}

export interface LabelOut {
  id: string
  name: string
  type: string
  messages_total: number
  messages_unread: number
  color?: LabelColor
}

export interface LabelCreate {
  name: string
  label_list_visibility?: 'labelShow' | 'labelShowIfUnread' | 'labelHide'
  message_list_visibility?: 'show' | 'hide'
  color?: LabelColor
}

export interface LabelUpdate {
  name?: string
  color?: LabelColor
}

export interface SuggestionOut {
  id: number
  account_id: number
  sender_email: string
  sender_domain: string
  email_count: number
  suggested_label: string
  suggested_action: string
  criteria_json: string
  ai_rationale: string | null
  status: 'pending' | 'accepted' | 'dismissed'
  created_at: string
}

export interface ScanStatus {
  last_run: string | null
  next_run: string | null
  pending_suggestions: number
  is_running: boolean
}

export interface SSEEvent {
  type: 'scan_complete' | 'suggestion_added' | 'account_status_changed'
  payload: unknown
}
