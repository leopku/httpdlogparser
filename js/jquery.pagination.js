/**
 * pagination 1.0 - jQuery Plug-in
 * 
 * Licensed under the GPL:
 *   http://gplv3.fsf.org
 *
 * Copyright 2009 stworthy [ stworthy@gmail.com ] 
 * 
 * Dependencies:
 * 	linkbutton
 * 
 */
(function($){
	$.fn.pagination = function(options) {
		
		if (typeof options == 'string'){
			switch(options){
				case 'options':
					return $.data(this[0], 'pagination').options;
			}
		}
		
		options = options || {};
		
		function contains(v, aa){
			for(var i=0; i<aa.length; i++){
				if (aa[i] == v) return true;
			}
			return false;
		}
		
		return this.each(function(){
			var opts;
			var state = $.data(this, 'pagination');
			if (state) {
				opts = $.extend(state.options, options);
			} else {
				opts = $.extend({}, $.fn.pagination.defaults, options);
				if (!contains(opts.pageSize, opts.pageList)){
					opts.pageSize = opts.pageList[0];
				}
				$.data(this, 'pagination', {
					options: opts
				});
			}
			
			var total = opts.total;
			var pageNumber = opts.pageNumber;
			var pageSize = opts.pageSize;
			var pageCount = Math.ceil(total/pageSize);
			
			var pager = $(this);
			render();
			
			function selectPage(page){
				return function(){
					pageNumber = page;
					if (pageNumber < 1) pageNumber = 1;
					if (pageNumber > pageCount) pageNumber = pageCount;
					
					opts.pageNumber = pageNumber;	// save the pageNumber state
					opts.pageSize = pageSize;
					opts.onSelectPage.call(pager, pageNumber, pageSize);
					
					render();
				};
			}
			
			function render(){
				pager.addClass('pagination').empty();
				var t = $('<table cellspacing="0" cellpadding="0" border="0"><tr></tr></table>').appendTo(pager);
				var tr = $('tr', t);
				
				var ps = $('<select class="pagination-page-list"></select>');
				for(var i=0; i<opts.pageList.length; i++) {
					$('<option></option>')
							.text(opts.pageList[i])
							.attr('selected', opts.pageList[i]==pageSize ? 'selected' : '')
							.appendTo(ps);
				}
				$('<td></td>').append(ps).appendTo(tr);
				
				$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
				$('<td><a icon="pagination-first"></a></td>').appendTo(tr);
				$('<td><a icon="pagination-prev"></a></td>').appendTo(tr);
				$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
				
				$('<span style="padding-left:6px;"></span>')
						.html(opts.beforePageText)
						.wrap('<td></td>')
						.parent().appendTo(tr);
				$('<td><input class="pagination-num" type="text" value="1" size="2"></td>').appendTo(tr);
				$('<span style="padding-right:6px;"></span>')
						.html(opts.afterPageText.replace(/{pages}/, pageCount))
						.wrap('<td></td>')
						.parent().appendTo(tr);
				
				$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
				$('<td><a icon="pagination-next"></a></td>').appendTo(tr);
				$('<td><a icon="pagination-last"></a></td>').appendTo(tr);
				$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
				
				if (opts.loading) {
					$('<td><a icon="pagination-loading"></a></td>').appendTo(tr);
				} else {
					$('<td><a icon="pagination-load"></a></td>').appendTo(tr);
				}
				
				if (opts.buttons){
					$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
					for(var i=0; i<opts.buttons.length; i++){
						var btn = opts.buttons[i];
						if (btn == '-') {
							$('<td><div class="pagination-btn-separator"></div></td>').appendTo(tr);
						} else {
							var td = $('<td></td>').appendTo(tr);
							$('<a href="javascript:void(0)"></a>')
									.addClass('l-btn')
									.css('float', 'left')
									.text(btn.text || '')
									.attr('icon', btn.iconCls || '')
									.bind('click', eval(btn.handler || function(){}))
									.appendTo(td)
									.linkbutton({plain:true});
						}
					}
				}
				
				var pinfo = opts.displayMsg;
				pinfo = pinfo.replace(/{from}/, pageSize*(pageNumber-1)+1);
				pinfo = pinfo.replace(/{to}/, Math.min(pageSize*(pageNumber),total));
				pinfo = pinfo.replace(/{total}/, total);
				$('<div class="pagination-info"></div>')
						.html(opts.displayMsg)
						.html(pinfo)
						.appendTo(pager);
				
				$('<div style="clear:both;"></div>').appendTo(pager);
				
				$('a', pager).attr('href','javascript:void(0)').linkbutton({plain:true});
				
				$('a[icon=pagination-first]', pager).bind('click', selectPage(1));
				$('a[icon=pagination-prev]', pager).bind('click', selectPage(pageNumber-1));
				$('a[icon=pagination-next]', pager).bind('click', selectPage(pageNumber+1));
				$('a[icon=pagination-last]', pager).bind('click', selectPage(pageCount));
				$('a[icon=pagination-load]', pager).bind('click', selectPage(pageNumber));
				$('a[icon=pagination-loading]', pager).bind('click', selectPage(pageNumber));
				if (pageNumber == 1){
					$('a[icon=pagination-first],a[icon=pagination-prev]', pager)
							.unbind('click')
							.linkbutton({disabled:true});
				}
				if (pageNumber == pageCount){
					$('a[icon=pagination-last],a[icon=pagination-next]', pager)
							.unbind('click')
							.linkbutton({disabled:true});
				}
				
				$('input.pagination-num', pager)
						.val(pageNumber)
						.keydown(function(e){
							if (e.keyCode == 13){
								pageNumber = parseInt($(this).val()) || 1;
								selectPage(pageNumber)();
							}
						});
				$('.pagination-page-list', pager).change(function(){
					pageSize = $(this).val();
					pageCount = Math.ceil(total/pageSize);
					pageNumber = opts.pageNumber;
					selectPage(pageNumber)();
				});
			}
		});
	};
	
	$.fn.pagination.defaults = {
		total: 1,
		pageSize: 10,
		pageNumber: 1,
		pageList: [10,20,30,50],
		loading: false,
		buttons: null,
		onSelectPage: function(pageNumber, pageSize){},
		
		beforePageText: 'Page',
		afterPageText: 'of {pages}',
		displayMsg: 'Displaying {from} to {to} of {total} items'
	};
})(jQuery);