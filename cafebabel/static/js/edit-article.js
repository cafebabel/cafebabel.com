class Tags {
  constructor(domContext) {
    this.list = domContext.querySelector('.tags .tags-list')
    this.values = Array.from(this.list.querySelectorAll('input')).map(
      input => input.value
    )
  }
  checkSubmission(query) {
    return query && !this._isTag(query)
  }
  add(query) {
    this.values = this.values.concat(query)
  }
  remove(query) {
    this.values = this.values.filter(value => value !== query)
  }
  _isTag(tag) {
    return this.values.includes(tag)
  }
  _createTagsList(container, tagValues) {
    tagValues.forEach((tagValue, index) =>
      container.appendChild(this._createTag(tagValue, index))
    )

    return container
  }
  _createTag(tagValue, index) {
    const li = document.createElement('li')
    const input = document.createElement('input')
    const a = document.createElement('a')
    input.type = 'hidden'
    input.name = `tag-${index + 1}`
    input.setAttribute('list', 'tags')
    input.value = tagValue
    li.append(tagValue)
    li.append(input)
    li.append(a)

    return li
  }
}

const tagButtonAdd = document.querySelector('.tags button.add')

tagButtonAdd.addEventListener('click', event => {
  event.preventDefault()
  const submission = event.target.previousSibling.value
  const tags = new Tags(document.querySelector('.tags'))
  if (tags.checkSubmission(submission)) tags.add(submission)
  displayTags(tags)
  Effect.fadeIn(document.querySelector('.tags .tags-list li:last-child'))
  document.querySelector('.tags input[name=tag-new]').value = ''
})

function handleSuggestion(tag) {
  const tagsSuggestion = document.querySelector('#tags-suggestions')
  tagsSuggestion.innerHTML = ''
  const li = document.createElement('li')
  li.append(tag.name)
  tagsSuggestion.appendChild(li)
  tagsSuggestion.classList.remove('inactive')
  tagsSuggestion.addEventListener('click', event => {
    const submission = event.target.innerText
    const tags = new Tags(document.querySelector('.tags'))
    if (tags.checkSubmission(submission)) tags.add(submission)
    displayTags(tags)
    li.remove()
    document.querySelector('.tags input[name=tag-new]').value = ''
    tagsSuggestion.classList.add('inactive')
  })
}

document
  .querySelector('.tags input[name=tag-new]')
  .addEventListener('keyup', event => {
    /* Return if arrow up, arrow down or enter are pressed */
    if (event.keyCode == 40 || event.keyCode == 38 || event.keyCode == 13)
      return
    document.querySelector('#tags-suggestions').innerHTML = ''
    const submission = event.target.value
    const languages = document.querySelector('#language')
    const language = languages.options[languages.selectedIndex].value
    if (submission.length < 3) return
    request(`/article/tag/suggest/?language=${language}&terms=${submission}`)
      .then(response => response.forEach(handleSuggestion))
      .catch(console.error.bind(console))
  })

function addTagsRemoveListener() {
  const tagsButtonRemove = document.querySelectorAll('.tags .tags-list li a')
  tagsButtonRemove.forEach(tagButtonRemove =>
    tagButtonRemove.addEventListener('click', event => {
      const tags = new Tags(document.querySelector('.tags'))
      const tagElement = event.target.parentNode
      tags.remove(tagElement.innerText)
      Effect.fadeOut(tagElement).then(response => displayTags(tags))
    })
  )
}

window.addEventListener('load', addTagsRemoveListener)

function displayTags(tags) {
  const container = tags.list.cloneNode(false)
  tags.list.replaceWith(tags._createTagsList(container, tags.values))
  addTagsRemoveListener()
}

class Effect {
  static fadeIn(element) {
    element.style.opacity = 0
    ;(function fade() {
      let val = parseFloat(element.style.opacity)
      if (!((val += 0.03) > 1)) {
        element.style.opacity = val
        requestAnimationFrame(fade)
      }
    })()
  }
  static fadeOut(element) {
    element.style.opacity = 1
    return new Promise((resolve, reject) => {
      ;(function fade() {
        if ((element.style.opacity -= 0.03) < 0) {
          element.style.display = 'none'
          resolve()
        } else {
          requestAnimationFrame(fade)
        }
      })()
    })
  }
}
