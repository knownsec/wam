$(function(){
  $(window).bind("scroll", function(){
    var scrollTopNum = $(document).scrollTop(),
    winHeight = $(window).height(),
    return_top = $("div.return-top");
    // 滚动条的垂直偏移大于 0 时显示，反之隐藏
    (scrollTopNum > 0) ? return_top.fadeIn("fast") : return_top.fadeOut("fast");
    if (!-[1,]&&!window.XMLHttpRequest) {
      return_top.css("top", scrollTopNum + winHeight - 200);
    }
  });
  $("div.return-top").click(function() {
    $("html, body").animate({ scrollTop: 0 }, 100);
  });
});
