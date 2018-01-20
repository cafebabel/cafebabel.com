class Tags {
  constructor() {
    this.context = document.querySelector('.tags')
  }
  get removeButtons() {
    return this._list.querySelectorAll('li button')
  }
  get buttonAdd() {
    return this.context.querySelector('button.add')
  }
  get suggestions() {
    return this.context.querySelector('#tags-suggestions')
  }
  get _languages() {
    return document.querySelector('#language')
  }
  get _language() {
    return this._languages.options[this._languages.selectedIndex].value
  }
  get _tags() {
    return this._list.querySelectorAll('input')
  }
  get _tagsNames() {
    return Array.from(this._tags).map(({ value }) => value)
  }
  get _list() {
    return this.context.querySelector('.tags-list')
  }
  get _fieldAdd() {
    return this.context.querySelector('input[name=tag-new]')
  }

  addNewTag(submission) {
    if (!submission || this._isTagName(submission)) return
    this._emptyAddField()
    this._inactiveSuggestionsList()
    this._render(this._tagsNamesAdd(submission))
  }
  removeTag(tagElement) {
    const submission = tagElement.textContent.trim()
    if (!this._isTagName(submission)) return
    this._render(this._tagsNamesRemove(submission))
  }
  handleSuggestion(submission) {
    this._request(submission).then(tagsApi =>
      this._createSuggestionList(tagsApi)
    )
  }
  _request(submission) {
    return request(
      `/article/tag/suggest/?language=${this._language}&terms=${submission}`
    ).catch(console.error.bind(console))
  }
  _isTagSaved(submission) {
    return this._request(submission).then(tagsApi =>
      tagsApi.some(tag => tag.name === submission)
    )
  }
  _isTagName(tagName) {
    return this._tagsNames.includes(tagName)
  }
  _tagsNamesAdd(tagName) {
    return this._tagsNames.concat([tagName])
  }
  _tagsNamesRemove(tagName) {
    return this._tagsNames.filter(selfTagName => selfTagName !== tagName)
  }
  _createSuggestionList(tagsApi) {
    this._activeSuggestionsList()
    const ul = this.suggestions.cloneNode(false)
    tagsApi.forEach(tag => {
      const li = `<li>${tag.name}</li>`
      ul.insertAdjacentHTML('afterbegin', li)
    })
    this._renderSuggestion(ul)
  }
  _createTagsList(container, tagValues) {
    return Promise.all(
      tagValues.map((tagValue, index) => this._createTag(tagValue, index))
    ).then(tagsList => {
      tagsList.forEach(tagItem => {
        container.insertAdjacentHTML('beforeend', tagItem)
      })
      return container
    })
  }
  _createTag(tagValue, index) {
    return this._isTagSaved(tagValue).then(
      isSave =>
        `<li ${isSave ? 'class=saved' : ''}>${tagValue}
          <input name=tag-${++index} list=tags value=${tagValue} type=hidden>
          <button type=button></button>
        </li>`
    )
  }
  _inactiveSuggestionsList() {
    this.suggestions.classList.add('inactive')
  }
  _activeSuggestionsList() {
    this.suggestions.classList.remove('inactive')
  }
  _emptySuggestions() {
    this.suggestions.innerHTML = ''
  }
  _emptyAddField() {
    this._fieldAdd.value = ''
  }
  _renderSuggestion(container) {
    this.suggestions.replaceWith(container)
    TagEventListener.addSuggestion()
  }
  _render(tagNames) {
    const container = this._list.cloneNode(false)
    this._createTagsList(container, tagNames).then(tagsList => {
      this._list.replaceWith(tagsList)
      if (!tagNames.length) return
      TagEventListener.addRemoveListener()
      TagEffect.fadeIn(this._list.querySelector('li:last-child'))
    })
  }
}

class TagEffect {
  static fadeIn(element) {
    function fade() {
      element.style.opacity = +element.style.opacity + 0.03
      if (element.style.opacity <= 1) {
        requestAnimationFrame(fade)
      }
    }
    element.style.opacity = 0
    fade()
  }
  static fadeOut(element) {
    function fade() {
      element.style.opacity = +element.style.opacity - 0.03
      if (element.style.opacity < 0) {
        element.style.display = 'none'
      } else {
        requestAnimationFrame(fade)
      }
    }
    element.style.opacity = 1
    fade()
  }
}

class TagEventListener {
  static clickAdd() {
    tags.buttonAdd.addEventListener('click', event => {
      event.preventDefault()
      const submission = event.target.previousSibling.value
      if (submission.length < 3) return
      tags.addNewTag(submission)
    })
  }
  static addSuggestion() {
    tags.suggestions.querySelectorAll('li').forEach(li =>
      li.addEventListener('click', event => {
        const submission = event.target.innerText
        tags.addNewTag(submission)
      })
    )
  }
  static addRemoveListener() {
    tags.removeButtons.forEach(button =>
      button.addEventListener('click', event => {
        const tagElement = event.target.parentElement
        tags.removeTag(tagElement)
      })
    )
  }
  static keyup() {
    const inputNewTag = document.querySelector('.tags input[name=tag-new]')
    inputNewTag.addEventListener('keyup', event => {
      event.preventDefault()
      /* Intercept -return- it's capture by 'click' for adding tags */
      if (event.keyCode == 38) return
      const submission = event.target.value
      if (submission.length < 3) return
      tags.handleSuggestion(submission)
    })
  }
}

const tags = new Tags()
window.addEventListener('load', () => {
  TagEventListener.keyup()
  TagEventListener.addRemoveListener()
  TagEventListener.clickAdd()
})
