var  ofc = $.query.get('ofc');
var site = ofc.substring(0, 4);
var date = ofc.substring(5, 15);

function createGrid(){
	if (site == '9949'){
	        $('#tt').datagrid({
	            title: 'Total Clicks of ' + date,
	            width: 800,
	            height: 600,
	            striped: true,
	            url: ofc,
	            fields: ['name', 'count', 'dest'],
	            columns: [[
	                {title: 'Name', field: 'name'},
	                {title: 'Click Count', field: 'count'},
	                {title: 'Destination', field: 'dest'}
	            ]],
	            sortName: 'count',
	            pagination: false
	        })
    	}
	else {
        	$('#tt').datagrid({
			title: 'Response Time per ISP',
			width: 800,
			height: 600,
			striped: true,
			url: ofc,
			fields: [
				'datetime','city','isp','domain','time', 'ref'
			],
			columns: [[
				{title:'Date & Time',field:'datetime',width:150},
				{title:'City',field:'city',width:150},
				{title:'ISP',field:'isp',width:150},
				{title:'Domain',field:'domain',width:100},
				{title:'Load Time',field:'time',width:100, align: 'right'},
	            {title: 'URL', field:'ref', width:200}
			]],
			sortName: 'time',
			sortOrder: 'asc',
			pagination: false/*,
			toolbar: [{
				text:'新增',
				iconCls:'icon-add',
				handler: newSale
			},{
				text:'修改',
				iconCls:'icon-edit',
				handler: editSale
			},'-',{
				text:'删除',
				iconCls:'icon-remove',
				handler: destroySale
			}]*/
		})
    }
}

var url;

function createDialog(){
	$('#dlg').dialog({
		closed: true,
		width: 400,
		height: 420,
		modal: true,
		buttons:{
			'保存': function(){
				$.ajax({
					url: url,
					type: 'post',
					data: $('#form1').serialize(),
					dataType:'json',
					success:function(data){
						if (data.success){
							$('#tt').datagrid('reload');	// 刷新列表数据
							$('#dlg').dialog({closed:true});// 关闭对话框
						} else {
							$.messager.alert('警告', data.msg, 'error');
						}
					}
				})
			},
			'取消': function(){
				$('#dlg').dialog({closed:true});
			}
		}
	})
}

function newSale(){
	$('#dlg').dialog({
		title: '新建销售数据',
		closed: false,
		href: '/test9/sale/create'
	});
	url = '/test9/sale/save';
}
function editSale(){
	var record = $('#tt').datagrid('getSelected');
	if (record){
		$('#dlg').dialog({
			title:'修改销售数据',
			closed:false,
			href:'/test9/sale/edit/'+record.orderNo+'?t='+new Date().getTime()
		});
		url = '/test9/sale/update/'+record.orderNo;
	} else {
		$.messager.alert('警告', '请先选择数据', 'warning');
	}
}
function destroySale(){
	var record = $('#tt').datagrid('getSelected');
	if (record){
		$.messager.confirm('删除确认','是否真的删除所选记录？', function(r){
			if (r){
				$.ajax({
					url:'/test9/sale/destroy/'+record.orderNo,
					type:'post',
					dataType:'json',
					success:function(){
						$('#tt').datagrid('reload');	// 刷新列表数据
					}
				})
			}
		});
	} else {
		$.messager.alert('警告', '请先选择数据', 'warning');
	}
	
}

$(function(){
	createGrid();
	createDialog();
})
