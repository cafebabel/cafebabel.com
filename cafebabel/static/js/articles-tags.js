class Tags {
  constructor() {
    this.context = document.querySelector('.tags')
    this.values = Array.from(this.list.querySelectorAll('input')).map(
      input => input.value
    )
  }
  get language() {
    const languages = document.querySelector('#language')
    return languages.options[languages.selectedIndex].value
  }
  get list() {
    return this.context.querySelector('.tags-list')
  }
  get removeButtons() {
    return this.list.querySelectorAll('li button')
  }
  get fieldAdd() {
    return this.context.querySelector('input[name=tag-new]')
  }
  get buttonAdd() {
    return this.context.querySelector('button.add')
  }
  get suggestions() {
    return this.context.querySelector('#tags-suggestions')
  }

  addNewTag(submission) {
    if (!submission || tags._isTag(submission)) return
    tags._addValue(submission)
    tags._emptyAddField()
    tags._inactiveSuggestionsList()
    tags._render()
  }
  removeTag(tagElement) {
    const submission = tagElement.innerText.trim()
    if (!tags._isTag(submission)) return
    tags._removeValue(submission)
    tags._render()
  }
  handleSuggestion(submission) {
    this._request(submission).then(tagsApi =>
      this._createSuggestionList(tagsApi)
    )
  }
  _request(submission) {
    return request(
      `/article/tag/suggest/?language=${this.language}&terms=${submission}`
    ).catch(console.error.bind(console))
  }
  _isTagSaved(submission) {
    return this._request(submission).then(tagsApi =>
      tagsApi.some(tag => tag.name === submission)
    )
  }
  _isTag(tag) {
    return this.values.includes(tag)
  }
  _addValue(query) {
    this.values.push(query)
  }
  _removeValue(query) {
    this.values = this.values.filter(value => value !== query)
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
    this.fieldAdd.value = ''
  }
  _renderSuggestion(container) {
    this.suggestions.replaceWith(container)
    TagEventListener.addSuggestion()
  }
  _render() {
    const container = this.list.cloneNode(false)
    this._createTagsList(container, this.values).then(tagsList => {
      this.list.replaceWith(tagsList)
      if (!this.values.length) return
      TagEventListener.addRemoveListener()
      TagEffect.fadeIn(this.list.querySelector('li:last-child'))
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
