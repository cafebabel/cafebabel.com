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
    const submission = tagElement.innerText
    if (!tags._isTag(submission)) return
    tags._removeValue(submission)
    tags._render()
  }
  handleSuggestion(submission) {
    this._request(submission)
      .then(tagsApi => this._createSuggestionList(tagsApi))
      .catch(console.error.bind(console))
  }
  _request(submission) {
    return request(
      `/article/tag/suggest/?language=${this.language}&terms=${submission}`
    )
  }
  _isTagSaved(tag) {
    return
  }
  _isTag(tag) {
    return this.values.includes(tag)
  }
  _addValue(query) {
    this.values = this.values.concat(query)
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
    tagValues.forEach((tagValue, index) =>
      container.insertAdjacentHTML(
        'beforeend',
        this._createTag(tagValue, index)
      )
    )

    return container
  }
  _createTag(tagValue, index) {
    return `<li>
        ${tagValue}
        <input name=tag-${++index} list=tags value=${tagValue} type=hidden>
        <button></button>
      </li>`
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
    this.list.replaceWith(this._createTagsList(container, this.values))
    TagEventListener.addRemoveListener()
    TagEffect.fadeIn(container.querySelector('li:last-child'))
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
        event.preventDefault()
        const tagElement = event.target.parentNode
        tags.removeTag(tagElement)
      })
    )
  }
  static keyup() {
    const inputNewTag = document.querySelector('.tags input[name=tag-new]')
    inputNewTag.addEventListener('keypress', event => {
      /* Return if arrow up, arrow down or enter are pressed */
      if (event.keyCode == 13) {
        return
      }
      if (event.keyCode == 40 || event.keyCode == 38) return
      const submission = event.target.value
      if (submission.length < 3) return
      tags.handleSuggestion(submission)
    })
  }
}

const tags = new Tags()
window.addEventListener('load', () => {
  TagEventListener.addRemoveListener()
  TagEventListener.clickAdd()
  TagEventListener.keyup()
})
