import enum


def getLang(key, params={}, lang='en'):
  langFile = __import__("language.%s"%lang)
  return getattr(langFile, lang).Lang.get(key,key).format(**params)

class Language(enum.Enum):
  en = "en"
  kh = "kh"

class LanguageKey:
  create_success  = "create_success"
  create_failed   = "create_failed"
  update_success  = "update_success"
  update_failed   = "update_failed"
  delete_success  = "delete_success"
  delete_failed   = "delete_failed"
  not_found       = "not_found"
  get_success     = "get_success"
  get_failed      = "get_failed"

  #Module
  company = 'company'
  branch  = 'branch'