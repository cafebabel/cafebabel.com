const tagButtonAdd = document.querySelector('.tags button.add')
const tagButtonRemove = document.querySelector('.tags button.remove')
const tagsList = document.querySelector('.tags .tagsList')

const Tag = {
  count: () => tagsList.querySelectorAll('li').length,
  createTag(tagValue) {
    const li = document.createElement('li')
    const input = document.createElement('input')
    li.append(tagValue)
    input.type = 'hidden'
    input.name = `tag-${Tag.count()}`
    input.setAttribute('list', 'tags')
    input.value = tagValue
    li.append(input)

    return li
  },
  tagValues: () => Array.from(tagsList.querySelectorAll('li')).map(li => li.innerText)
}

tagButtonAdd.addEventListener('click', (event) => {
  event.preventDefault()
  const tagValue = event.target.previousElementSibling.value
  if (!tagValue || Tag.tagValues().includes(tagValue)) return
  tagsList.appendChild(Tag.createTag(tagValue))
})

