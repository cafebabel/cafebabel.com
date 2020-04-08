/* Go to anchor smoothly */
var html, body
window.onload = function() {
  const links = document.links
  html = document.documentElement
  body = document.body

  if (links) {
    for (var i = 0; i < links.length; i++) {
      links[i].onclick = function(event) {
        console.log('link')
        //getting current scroll position
        var scrollTop = Math.round(body.scrollTop || html.scrollTop)
        if (this.hash !== "") {
          //preventing default anchor click behavior
          event.preventDefault()

          //getting element with id found in hash
          var hashElement = document.getElementById(this.hash.substring(1))

          var hashElementTop = 0
          var obj = hashElement
          if (obj) {
            while (obj.offsetParent) {
              hashElementTop += obj.offsetTop
              obj = obj.offsetParent
            }
            //getting element's position
            hashElementTop = Math.round(hashElementTop)

            scroll(scrollTop, hashElementTop, this.hash)
          }
        }
      }
    }
  }
}
function scroll(from, to, hash) {
  var timeInterval = 1 //in ms
  var prevScrollTop
  var increment = to > from ? 25 : -25
  var scrollByPixel = setInterval(function() {
    var scrollTop = Math.round(body.scrollTop || html.scrollTop)

    if (
        prevScrollTop == scrollTop ||
        (to > from && scrollTop >= to) ||
        (to < from && scrollTop <= to)
    ) {
      clearInterval(scrollByPixel)
      window.location.hash = hash
    } else {
      body.scrollTop += increment
      html.scrollTop += increment

      prevScrollTop = scrollTop
    }
  }, timeInterval)
}
