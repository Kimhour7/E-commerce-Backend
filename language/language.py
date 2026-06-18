import enum


def getLang(key, params={}, lang='en'):
  langFile = __import__("language.%s"%lang)
  return getattr(langFile, lang).Lang.get(key,key).format(**params)

class Language(enum.Enum):
  en = "en"
  kh = "kh"

class LanguageKey:
  success_message = "success_message"
  company_create_failed = "company_create_failed"
  company_update_success = "company_update_success"
  company_update_failed = "company_update_failed"
  company_delete_success = "company_delete_success"
  company_not_found = "company_not_found"