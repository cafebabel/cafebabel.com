class Tags {
  constructor(domContext) {
    this.list = domContext.querySelector('ul')
    this.values = Array.from(this.list.querySelectorAll('li')).map(li => li.innerText)
  }
  checkSubmission(query) {
    return query && ! this._isTag(query)
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
    tagValues.forEach((tagValue, index) => container.appendChild(this._createTag(tagValue, index)))

    return container
  }
  _createTag(tagValue, index) {
    const li = document.createElement('li')
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = `tag-${index + 1}`
    input.setAttribute('list', 'tags')
    input.value = tagValue
    li.append(tagValue)
    li.append(input)

    return li
  }
}

const tagButtonAdd = document.querySelector('.tags button.add')

tagButtonAdd.addEventListener('click', (event) => {
  event.preventDefault()
  const submission = event.target.previousSibling.value
  const tags = new Tags(document.querySelector('.tags'))
  if (tags.checkSubmission(submission)) tags.add(submission)
  displayTags(tags)
  event.target.previousSibling.value = ''
})

function addTagsRemoveListener() {
  const tagsButtonRemove = document.querySelectorAll('.tags ul')
  tagsButtonRemove.forEach(tagButtonRemove => tagButtonRemove.addEventListener('click', (event) => {
    const tags = new Tags(document.querySelector('.tags'))
    tags.remove(event.target.innerText)
    displayTags(tags)
  }))
}

function displayTags(tags) {
  const container = tags.list.cloneNode(false)
  tags.list.replaceWith(tags._createTagsList(container, tags.values))
  document.querySelector('.tags ul li:last-child').classList.add('fadeIn')
  addTagsRemoveListener()
}
