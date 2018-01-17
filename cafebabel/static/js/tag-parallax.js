const parallax = document.querySelector('.tag-header-image')
if (parallax) {
  window.addEventListener('scroll', () => {
    const scrolledHeight = window.pageYOffset
    const limit = parallax.offsetTop + parallax.offsetHeight
    if (scrolledHeight > parallax.offsetTop && scrolledHeight <= limit) {
      parallax.style.backgroundPositionY = `${(parallax.offsetTop -
        scrolledHeight) /
        3}px`
    } else {
      parallax.style.backgroundPositionY = '0'
    }
  })
}
