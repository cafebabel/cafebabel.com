const container = document.querySelector('.tag-header')
const imgUrl = container.getAttribute('data-image')

addBackgroundImage(container, imgUrl)
parallax(imgUrl)

function parallax(imgUrl) {
  const container = document.querySelector('.tag-header.image')
  const height = getHeight(imgUrl)

  if (!container) return
  window.addEventListener('scroll', () => {
    const scrolledHeight = window.pageYOffset
    const top = container.offsetTop - height * 2
    container.style.backgroundPositionY = `${(top - scrolledHeight) / 3}px`
  })
}

function addBackgroundImage(container, imgUrl) {
  if (imgUrl) {
    container.classList.add('image')
    container.style.backgroundImage = `url(${imgUrl})`
  } else {
    container.classList.add('default')
  }
}

function getHeight(url) {
  const img = new Image()

  img.addEventListener('load', () => img.height)
  img.src = url

  return img.height
}
