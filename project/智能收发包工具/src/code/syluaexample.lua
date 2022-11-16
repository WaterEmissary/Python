-- assign the lua-lib-file's searching pattern
package.cpath = package.path
package.path  = (debug.getinfo(1, "S").source:sub(2):match("(.*/)") or "./") .. '?.lua;/userdata/proto/?.lua'

log = require("log") -- this log is also used by THE following gmoe
log.usecolor = false
log.outfile  = 'nil' -- nil: for output to console /userdata/aprotocal_lua.log
log.level    = "trace"                       -- "trace", "debug", "info", "warn", "error", "fatal",


local verberno={}	-- 版本号

-- 发送命令
local SendPack =
{

}
-- 控制命令
local CtrlPack =
{

}
-- 关联ID
local SigConfig =
{

}
-- 类CFG
local GroupType =
{

}

local PublicParam={0,0,0,0,0,0,0,0,0,0,0}
function Ctrl_AODO_Send_cmd(addr, ctrlnumber, val )	 -- 控制命令部分,自行实现
	local NodeID = tonumber(ctrlnumber)
	local DataBuf={}
	log.info("NodeID= "..NodeID)
	--[[例：
		if( NodeID==201 ) then	
			Length = 22
			DataBuf[0] = (val*1000)//256
			DataBuf[1] = (val*1000)%256
			DataBuf[2] = PublicParam[2]*1000//256
			DataBuf[3] = PublicParam[2]*1000%256
			DataBuf[4] = PublicParam[3]//256
			DataBuf[5] = PublicParam[3]%256
			DataBuf[6] = PublicParam[4]//256
			DataBuf[7] = PublicParam[4]%256
			DataBuf[8] = PublicParam[5]*1000//256
			DataBuf[9] = PublicParam[5]*1000%256
			DataBuf[10] = PublicParam[6]*1000//256
			DataBuf[11] = PublicParam[6]*1000%256
			DataBuf[12] = PublicParam[7]*1000//256
			DataBuf[13] = PublicParam[7]*1000%256
			DataBuf[14] = PublicParam[8]*1000//256
			DataBuf[15] = PublicParam[8]*1000%256
			DataBuf[16] = PublicParam[9]//256
			DataBuf[17] = PublicParam[9]%256
			DataBuf[18] = PublicParam[10]//256
			DataBuf[19] = PublicParam[10]%256
			DataBuf[20] = PublicParam[11]//256
			DataBuf[21] = PublicParam[11]%256
			return YDT1363_Send_Ctrl_Cmd(addr,Length,DataBuf,1)
		end
	]]

end
function Analog_Rev_cmd(ParamInfo, recvBuf, scanIdx) -- 接收数据并解析,自行实现
	local RecvData={}
	local Version = ParamInfo[1]
	local Addr    = ParamInfo[2]
	local CID1 	  = ParamInfo[3]
	local CID2 	  = ParamInfo[4]
	local Length  = ParamInfo[5]
	local recvBufLen = string.len(recvBuf)

	--[[例：
		if( CID2==0x54 ) then					-- 获取系统参数(D7_54)	
			if( Length>=20 ) then
				local DataOffset = 1
				for k=1,10 do
					if( (k==3) or (k==4) or (k==9) or (k==10) ) then
						GroupType[49+(k-1)] = PCM_DEV_Get_U16(GroupType[49+(k-1)], recvBuf, recvBufLen, DataOffset, RecvData)
					else
						GroupType[49+(k-1)] = PCM_DEV_Get_U16(GroupType[49+(k-1)], recvBuf, recvBufLen, DataOffset, RecvData,"/1000")
					end
					PublicParam[k] = RecvData[1] 
					DataOffset = DataOffset + 2
				end
				PublicParam[11] = PCM_DEV_Get_U16(nil, recvBuf, recvBufLen, DataOffset, RecvData)
				DataOffset = DataOffset + 2
			end
		end
	--]]


end










--[[
	下列函数,则为SDK接口函数,一般不做任何改动,
	上列函数,则为拓展的函数,遥调遥控和遥信遥测的设置与获取的函数
--]]
function init ()						-- 无需改动			
    local sig_cnt  = 0
	local scanCmdNum = 0
	local Number = {}	-- 关联点位号
    local sig_list = ""
    for k,v in pairs(SigConfig) do
		local configid = string.sub(SigConfig[k], 2, 11) -- 信号ID
		local NodeNum  = find_number(SigConfig[k])		 -- 信号ID的数量
		find_NodeId(SigConfig[k], Number, NodeNum)	     -- 关联的信号ID对于的点位号

		local offset = 0
		for m=1,NodeNum do
			if( Number[m] ~= "0" ) then
				local meterIdList = tonumber(configid)
				meterIdList = meterIdList + offset
				local String =  string.format("%9s",meterIdList)
				String = "0"..String
				sig_list = sig_list..String..","
				sig_cnt  = sig_cnt + 1
			end
			offset = offset + 1
		end
    end

    if (string.len(sig_list) > 0) then -- cut the last ','
        sig_list  = string.sub(sig_list, 1, -2)
    end

	for k,v in pairs(SendPack) do	scanCmdNum = scanCmdNum + 1		end
	local version = string.format("{\"version\":\"%s\",\"model\":\"%s\",\"vendorName\":\"%s\",\"name\":\"%s\"}",VERSION, MODEL, "jsya", DEV_NAME)

	return scanCmdNum,
           DEV_NAME,
           version,
           sig_list,
           sig_cnt
end
function uninit() 						-- 无需改动
	return 0
end
function set_AODO(addr, meterid, val)	-- 无需改动
    if (not string.match(meterid, "^0%d%d%d%d%d%d%d%d%d$")) then
        log.error("meterid format error as "..meterid)
        return ""
    end
    local SendPackString=""
	local Number = {}	-- 关联点位号
	for k,v in pairs(SigConfig) do
		local configid = string.sub(SigConfig[k], 2, 11) -- 信号ID
		local NodeNum  = find_number(SigConfig[k])		 -- 信号ID的数量
		find_NodeId(SigConfig[k], Number, NodeNum)	     -- 关联的信号ID对于的点位号
		local offset = 0
		for m=1,NodeNum do
			if( Number[m] ~= "0" ) then
				local meterIdList = tonumber(configid)
				meterIdList = meterIdList + offset
				local String =  string.format("%9s",meterIdList)
				String = "0"..String
				if( String == meterid ) then
					SendPackString = Ctrl_AODO_Send_cmd(addr, Number[m], val)
					return SendPackString
				end
			end
			offset = offset + 1
		end
    end
	log.error("meterid was not be-supported: "..meterid)
    return ""
end
function parse_AODO(ack_package)		-- 无需改动	
    data, errmsg = YDT1363_depack(ack_package)
    if (data == nil) then
        log.error("parse_AODO: "..errmsg)
        return -1
    else
        return 0
    end
end
function scan (step, addr)				-- 无需改动
	local number=0
	for k,v in pairs(SendPack) do	number = number + 1		end

	if( step <= number ) then
		local VerNo = string.sub(SendPack[step], 3, 4)
		local verno  = tonumber(VerNo,16)
		if(verberno[1]==nil) then
			ver=verno
		else
			ver=verberno[1]
		end

		local CID1H = string.sub(SendPack[step], 13, 14)
		local CID2H = string.sub(SendPack[step], 18, 19)
		local CID1  = tonumber(CID1H,16)
		local CID2  = tonumber(CID2H,16)

		local DataLen = string.len(SendPack[step]) + 1
		local ParamLen = (DataLen//5) - 4
		local DataParam=""
		local offset = 23
		for k=1,ParamLen do
			local ParmData = string.sub(SendPack[step], offset, offset+1)
			local Param  = tonumber(ParmData,16)
			offset = offset + 5
			Data = string.char(Param)
			DataParam = DataParam..Data
		end
		return 0,  YDT1363_pack(ver, addr, CID1, CID2, DataParam)
	end
	return 0,""
end
function parse (step, package)			-- 无需改动
	local number=0
	local ParamInfo={}

	for k,v in pairs(SendPack) do	number = number + 1		end
    if (not in_range(step, 1, number)) then
        log.error("parse: scan-step is out of range: "..tostring(step))
        return 0,'{"meterInfo":[]}'
    end

    data, errmsg = YDT1363_depack(package)
    if (data == nil) then
        log.error("YDT1363协议: ".."< "..DEV_NAME.." > 回包报错: "..step.."  错误原因: "..errmsg)
        return 1,'{"meterInfo":[]}'
    end

	ParamInfo[1] = tonumber(string.sub(package, 2, 3),16) 				-- Version
	ParamInfo[2] = tonumber(string.sub(package, 4, 5),16) 				-- Addr
	ParamInfo[3] = tonumber(string.sub(package, 6, 7),16) 				-- CID1
	ParamInfo[4] = tonumber(string.sub(package, 8, 9),16) 				-- CID2
	ParamInfo[5] = (tonumber(string.sub(package, 10, 13),16)&0x0FFF)//2	-- Length

    local json = '{"meterInfo":[\n'
	if( step <= number ) then
		log.trace("YDT1363协议: ".."< "..DEV_NAME.." > 命令解析: "..step.."\n"..package)
		Analog_Rev_cmd(ParamInfo, data, step)

		for k,v in pairs(GroupType) do
			if( string.find(v,":") ~= nil ) then
			--{
				local GroupInfo={}
				find_GroupType(v,GroupInfo)

				for i,s in pairs(SigConfig) do
					local GroupNumber = {}	-- 关联点位号
					local configid = string.sub(s, 2, 11) 	-- 信号ID
					local NodeNum  = find_number(s)		 	-- 信号ID的数量
					find_NodeId(s, GroupNumber, NodeNum)	-- 关联的信号ID对于的点位号

					local offset = 0
					for m=1,NodeNum do
						if( GroupNumber[m] == GroupInfo[1] ) then
							local meterIdList = tonumber(configid) + offset
							local String = "0"..string.format("%9s",meterIdList)
							if( GroupInfo[2]=="81" ) then	-- 字符串
								json = json..string.format("  {\"meterId\":\"%s\", \"type\":\"string\", \"val\":\"%s\"}, \n",String,GroupInfo[6])
							else							-- double型数据
								json = json..string.format("  {\"meterId\":\"%s\", \"type\":\"double\", \"val\":\"%s\"}, \n",String,GroupInfo[6])
							end
						end
						offset = offset + 1
					end
				end
				log.info("解析数据(回包"..step.."): "..v)
				GroupType[k] = Clear_GroupType(v)
			--}	
			end
		end
	end

	local meterIdNo = select(2, string.gsub(json, "meterId", ""))
	if( meterIdNo == 0 ) then
		json = json..'\n]}'
	else
		json,to_drop = json:match'(.*)(,.*\n)' -- erease the ',' at last line
		json = json..'\n]}'
	end
    log.trace("回包"..step.." ,".."上送给平台数据: ".."\n"..json)
    return select(2, string.gsub(json, "meterId", "")), json
end

function in_range(v, min, max) return (v >= min and v <= max) end
function trim(s)               return s:match "^%G-(%g*)%G-$"  end
function find_number(n)
	local start = string.find(n,",")
	local top   = string.find(n,",{")
	local Number = string.sub(n, start+1, top-1)
	local Data   = tonumber(Number)
	return Data
end
function find_NodeId(n, data, Num)
	local start   = string.find(n,",{")
	local top     = string.find(n,"}}")
	local cutdata = string.sub(n, start+2, top-1)

	cutdata = cutdata..","
	local offset = 1
	for k=1,Num do
		DataVal =  string.find(cutdata, ",", offset)
		data[k] =  string.sub(cutdata, offset, DataVal-1)
		offset  =  DataVal + 1
	end
end
function InsertVal_To_GroupType(GroupNo, val)	-- 将解析后的数据插入到 GroupType 表中(XX,XX,XX,XX:val)
	local ValSeat = string.find(GroupNo,":")
	if( ValSeat == nil ) then
		local start   = string.find(GroupNo,"{")
		local top     = string.find(GroupNo,"}")
		local cutdata = string.sub(GroupNo, start+1, top-1)
		cutdata = "{"..cutdata..":"..val.."}"
		return cutdata
	else
		local start   = string.find(GroupNo,"{")
		local cutdata = string.sub(GroupNo, start+1, ValSeat-1)
		cutdata = "{"..cutdata..":"..val.."}"
		return cutdata
	end
	return GroupNo
end
function find_GroupType(Group, data)
	local GroupString = string.gsub(Group,":",",",1)
	local start   = string.find(GroupString,"{")
	local top     = string.find(GroupString,"}")
	local cutdata = string.sub(GroupString, start+1, top-1)
	cutdata = cutdata..","

	local offset = 1
	for k=1,6 do
		DataVal =  string.find(cutdata, ",", offset)
		data[k] =  string.sub(cutdata, offset, DataVal-1)
		offset  =  DataVal + 1
	end
end
function Clear_GroupType(Group)
	local top   = string.find(Group,":")
	local cutdata = string.sub(Group, 1, top-1)
	cutdata = cutdata.."}"
	return cutdata
end


--[[
固定参数: Group[GroupType对应的点]   Data[接收包的有效数据]  Len[接收包的有效数据长度]  Offset[数据偏移字节]  RecvData[解析数据返回值]
可变参数：
0个参数：
	无参数[RecvData的值为整数]
1个参数： 
	类型1(string): "+0"  "-0"  "*1"  "/1"	
	类型2(string): ">>1" "<<1"
2个参数：
	类型1(string,string)： [ "+0","*1" ]
	类型2(string,number)： [ "+",  1 ] [ "-", 1 ] [ "*", 1 ] [ "/",1 ]  string长度为1
3个参数：
	类型1(string,string,string):  [ "+0","*1","/1" ]
	类型2(string,number,string):  [ "+",0,"*1"     ]  [ "-",0,"*1"     ]  [ "*",0,"*1"     ]  [ "/",0,"*1"     ] string1长度为1
	类型3(string,number,number):  [ "!=0",1,0      ]  [ "==0",1,0      ]  [ "&3",1,0       ]					 string1长度为>=2	
4个参数：
	类型1(string,number,string,number)		 :  [ "+",0,"*",1        ]  
5个参数：
	类型1(string,number,string,number,string):  [ "+",0,"*",1,"*10"  ]  
返回值  : 参数Group为nil,返回值为解析数据返回值   参数Group非nil,返回值为将解析后是数据插入到Group末尾	
--]]
function PCM_DEV_Get_F32(Group, Data, Len, Offset, RecvData, ...)
--{
	local arg={...}
	local Flag = #arg
	RecvData[1] = 0
	if( Group==nil ) then
	--{
		if( Len >= (Offset+3) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+3)
			if( DataValString=="\xFF\xFF\xFF\xFF") then DataValString = "\x00\x00\x00\x00" end
			local DataVal = string.format("%.3f", string.unpack("f",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
		--}
		end
		return RecvData[1]
	--}
	else
	--{
		if( Len >= (Offset+3) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+3)
			if( DataValString=="\xFF\xFF\xFF\xFF") then DataValString = "\x00\x00\x00\x00" end
			local DataVal = string.format("%.3f", string.unpack("f",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end

			DataVal     = RecvData[1]
			return InsertVal_To_GroupType(Group,string.format("%.3f", DataVal))
		--}
		else
			return Group
		end
	--}
	end
--}
end
function PCM_DEV_Get_U8(Group, Data, Len, Offset, RecvData, ...)
--{
	local arg={...}
	local Flag = #arg
	RecvData[1] = 0
	if( Group==nil ) then
	--{
		if( Len >= Offset ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset)
			local DataVal = string.format("%.3f", string.unpack("B",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
		--}
		end
		return RecvData[1]
	--}
	else
	--{
		if( Len >= Offset ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset)
			local DataVal = string.format("%.3f", string.unpack("B",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end

			DataVal     = RecvData[1]
			return InsertVal_To_GroupType(Group,string.format("%.3f", DataVal))
		--}
		else
			return Group
		end
	--}
	end
--}
end
function PCM_DEV_Get_U16(Group, Data, Len, Offset, RecvData, ...)
--{
	local arg={...}
	local Flag = #arg
	RecvData[1] = 0
	if( Group==nil ) then
	--{
		if( Len >= (Offset+1) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+1)
			local DataVal = string.format("%.3f", string.unpack(">I2",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
		--}
		end
		return RecvData[1]
	--}
	else
	--{
		if( Len >= (Offset+1) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+1)
			local DataVal = string.format("%.3f", string.unpack(">I2",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
			DataVal     = RecvData[1]
			return InsertVal_To_GroupType(Group,string.format("%.3f", DataVal))
		--}
		else
			return Group
		end
	--}
	end
--}
end
function PCM_DEV_Get_U32(Group, Data, Len, Offset, RecvData, ...)
--{
	local arg={...}
	local Flag = #arg
	RecvData[1] = 0
	if( Group==nil ) then
	--{
		if( Len >= (Offset+3) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+3)
			if( DataValString=="\xFF\xFF\xFF\xFF") then DataValString = "\x00\x00\x00\x00" end
			local DataVal = string.format("%.3f", string.unpack(">I4",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
		--}
		end
		return RecvData[1]
	--}
	else
	--{
		if( Len >= (Offset+3) ) then
		--{
			local DataValString = string.sub(Data,Offset,Offset+3)
			if( DataValString=="\xFF\xFF\xFF\xFF") then DataValString = "\x00\x00\x00\x00" end
			local DataVal = string.format("%.3f", string.unpack(">I4",DataValString))

			if( Flag==0 ) then			-- 0个参数
			--{
				RecvData[1] = DataVal//1
			--}
			elseif( Flag==1 ) then		-- 1个参数
			--{
				local ValLen  = string.len(arg[1])
				if( (type(arg[1])=="string") and (ValLen>=1)  ) then
				--{
					local Symbol  = string.sub(arg[1],1,1)
					if( ((Symbol==">") or (Symbol=="<")) and (ValLen>=3) ) then
					--{
						local Values  = string.sub(arg[1],3,ValLen)
						local ValHex  = tonumber(Values)
						local CompareVal =  DataVal//1
						if( Symbol==">" ) then 		-- 左移
							RecvData[1] = ((CompareVal>>ValHex)&1)
						elseif( Symbol=="<" ) then 	-- 右移
							if( ((CompareVal<<ValHex)&0x80)==0x80 ) then RecvData[1]=1 else RecvData[1]=0 end
						else
							RecvData[1] = 0
						end
					--}
					elseif( ValLen>=2 ) then
					--{
						local Values  = string.sub(arg[1],2,ValLen)
						local ValHex  = tonumber(Values)
						if( Symbol=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex
						elseif( Symbol=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex
						elseif( Symbol=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex
						elseif( Symbol=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex
						else
							RecvData[1] = 0
						end
					--}
					else
						RecvData[1] = 0
					end
				--}
				end
			--}
			elseif( Flag==2 ) then		-- 2个参数	
			--{	
				if( (type(arg[1])=="string") and (type(arg[2])=="string")) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				end
			--}	
			elseif( Flag==3 ) then		-- 3个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="string") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1>=2 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						local Values1  = string.sub(arg[1],2,ValLen1)
						local ValHex1  = tonumber(Values1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + ValHex1
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - ValHex1
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * ValHex1
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / ValHex1
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen2  = string.len(arg[2])
					if( ValLen2>=2 ) then
					--{
						local Symbol2  = string.sub(arg[2],1,1)
						local Values2  = string.sub(arg[2],2,ValLen2)
						local ValHex2  = tonumber(Values2)
						if( Symbol2=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex2
						elseif( Symbol2=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex2
						elseif( Symbol2=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex2
						elseif( Symbol2=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex2
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen3  = string.len(arg[3])
					if( ValLen3>=2 ) then
					--{
						local Symbol3  = string.sub(arg[3],1,1)
						local Values3  = string.sub(arg[3],2,ValLen3)
						local ValHex3  = tonumber(Values3)
						if( Symbol3=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex3
						elseif( Symbol3=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex3
						elseif( Symbol3=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex3
						elseif( Symbol3=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex3
						else
							RecvData[1] = 0
						end
					--}
					end
				--}
				elseif( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					local StringSymbol=""
					if( ValLen1>=1 ) then
						StringSymbol  = string.sub(arg[1],1,1)
					end

					if( ((StringSymbol=="!") or (StringSymbol=="=")) and (ValLen1>=3) ) then
					--{
						local Symbol1  = string.sub(arg[1],1,2)
						local Values1  = string.sub(arg[1],3,ValLen1)
						local ValHex1  = tonumber(Values1)
						local CompareVal =  DataVal//1
						if( Symbol1=="!=" ) then 		-- 不等于
							if( CompareVal~=ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						elseif( Symbol1=="==" ) then 	-- 等于
							if( CompareVal==ValHex1 ) then RecvData[1]=arg[2] else RecvData[1]=arg[3] end
						else
							RecvData[1] = 0
						end
					--}
					elseif( (StringSymbol=="&") and (ValLen1>=2) ) then
					--{
						local Symbol3  = string.sub(arg[1],1,1)
						local Values3  = string.sub(arg[1],2,ValLen1)
						local ValHex3  = tonumber(Values3)
						local CompareVal =  DataVal//1
						if( (CompareVal & ValHex3)==ValHex3 ) then
							RecvData[1]=arg[2]
						else
							RecvData[1]=arg[3]
						end
					--}
					end
				--}
				end
			--}
			elseif( Flag==4 ) then		-- 4个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			elseif( Flag==5 ) then		-- 5个参数	
			--{
				if( (type(arg[1])=="string") and (type(arg[2])=="number") and (type(arg[3])=="string") and (type(arg[4])=="number") and (type(arg[5])=="string") ) then
				--{
					local ValLen1  = string.len(arg[1])
					if( ValLen1==1 ) then
					--{
						local Symbol1  = string.sub(arg[1],1,1)
						if( Symbol1=="+" ) then 		-- 加
							RecvData[1] = DataVal + arg[2]
						elseif( Symbol1=="-" ) then 	-- 减
							RecvData[1] = DataVal - arg[2]
						elseif( Symbol1=="*" ) then 	-- 乘
							RecvData[1] = DataVal * arg[2]
						elseif( Symbol1=="/" ) then 	-- 除
							RecvData[1] = DataVal / arg[2]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen4  = string.len(arg[3])
					if( ValLen4==1 ) then
					--{
						local Symbol4  = string.sub(arg[3],1,1)
						if( Symbol4=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + arg[4]
						elseif( Symbol4=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - arg[4]
						elseif( Symbol4=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * arg[4]
						elseif( Symbol4=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / arg[4]
						else
							RecvData[1] = 0
						end
					--}
					end

					local ValLen5  = string.len(arg[5])
					if( ValLen5>=2 ) then
					--{
						local Symbol5  = string.sub(arg[5],1,1)
						local Values5  = string.sub(arg[5],2,ValLen5)
						local ValHex5  = tonumber(Values5)
						if( Symbol5=="+" ) then 		-- 加
							RecvData[1] = RecvData[1] + ValHex5
						elseif( Symbol5=="-" ) then 	-- 减
							RecvData[1] = RecvData[1] - ValHex5
						elseif( Symbol5=="*" ) then 	-- 乘
							RecvData[1] = RecvData[1] * ValHex5
						elseif( Symbol5=="/" ) then 	-- 除
							RecvData[1] = RecvData[1] / ValHex5
						else
							RecvData[1] = 0
						end
					--}
					end

				--}
				end
			--}
			end
			DataVal     = RecvData[1]
			return InsertVal_To_GroupType(Group,string.format("%.3f", DataVal))
		--}
		else
			return Group
		end
	--}
	end
--}
end
function PCM_DEV_Get_SysTime(Group, Data, Len, Offset)
	if( Len >= (Offset+6) ) then
		local yy,M,d,h,m,s = string.gmatch(Data, "(..)(.)(.)(.)(.)(.)")()
		local t={year=string.unpack(">I2",yy),month=string.byte(M),day=string.byte(d),hour=string.byte(h),min=string.byte(m),sec=string.byte(s),isdst=false}
		local DataVal = string.format("%.1f", os.time(t))
		local InsertString = InsertVal_To_GroupType(Group,DataVal)
		return InsertString
	end
	return Group
end
-- 参数OffsetLen为字符串长度
function PCM_DEV_Get_String(Group, Data, Len, Offset, OffsetLen)
	if( Len >= (Offset+OffsetLen-1) ) then
		local DataValString = string.sub(Data,Offset,(Offset+OffsetLen-1))
		local DataVal = trim(DataValString)
		local InsertString = InsertVal_To_GroupType(Group,DataVal)
		return InsertString
	else
		return Group
	end
end


function Float_To_Hex(val)									--浮点数转换成4字节16进制数
	flaotval = string.pack("f",val)
	val  = string.unpack("i4",flaotval)
	Hex1 = (val&0xFF)
	Hex2 = ((val>>8)&0xFF)
	Hex3 = ((val>>16)&0xFF)
	Hex4 = ((val>>24)&0xFF)
	return Hex1,Hex2,Hex3,Hex4
end
function YDT1363_Send_Ctrl_Cmd(addr, Paramlen, buf, step)	--输入参数:地址,参数长度,参数xx,命令序号   返回值  :发包命令
	local number=0
	for k,v in pairs(CtrlPack) do	number = number + 1		end
	if( step>number ) then return nil end

	local VerNo = string.sub(CtrlPack[step], 3, 4)
	local verno  = tonumber(VerNo,16)
	if(verberno[1]==nil) then
		ver=verno
	else
		ver=verberno[1]
	end

	local CID1H = string.sub(CtrlPack[step], 13, 14)
	local CID2H = string.sub(CtrlPack[step], 18, 19)
	local CID1  = tonumber(CID1H,16)
	local CID2  = tonumber(CID2H,16)
	log.info("CID1= "..CID1)
	log.info("CID2= "..CID2)
	log.info("Paramlen= "..Paramlen)

	local DataParam=""
	for k=1,Paramlen do
		Data = string.char(buf[k-1])
		DataParam = DataParam..Data
	end
	log.info("DataParam= "..DataParam)
	return YDT1363_pack(ver, addr, CID1, CID2, DataParam)
end

function HexToAscii(oBuf, dBuf, oLen, IsCapital)
	if( IsCapital == 1 ) then
		Add = 0
	else
		Add = 0x20
	end

	local oBufOffset = 1
	local dBufOffset = 1

	for Count=1,oLen do
		if ( ((oBuf[oBufOffset] >> 4) & 0xF) > 9 ) then
			dBuf[dBufOffset]		= Add + 0x41 + ((oBuf[oBufOffset] >> 4) & 0xF) - 10
		else
			dBuf[dBufOffset]		= 0x30 + ((oBuf[oBufOffset] >> 4) & 0xF)
		end

		dBufOffset	= dBufOffset + 1

		if ((oBuf[oBufOffset] & 0xF) > 9) then
			dBuf[dBufOffset]		= Add + 0x41 + (oBuf[oBufOffset] & 0xF) - 10
		else
			dBuf[dBufOffset]		= 0x30 + (oBuf[oBufOffset] & 0xF)
		end
		oBufOffset	= oBufOffset + 1
		dBufOffset	= dBufOffset + 1

	end
end
function YDT1363_pack( Ver, Addr, CID1, CID2, Param )	-- 电总协议组包
	local SendData={}
	local pBuf={}
	local ConvertBuf={}
	local ChecksumBuf={}
	SendData[1] = Ver
	SendData[2] = Addr
	SendData[3] = CID1
	SendData[4] = CID2
	ParamLen = string.len(Param)
	Len 	 = ParamLen*2
	LenChecksum		= (Len & 0xF) + ((Len >> 4) & 0xF) + ((Len >> 8) & 0xF)
	LenChecksum		= LenChecksum % 16
	LenChecksum		= (~LenChecksum + 1) & 0xF
	Len				= (LenChecksum << 12) + Len
	SendData[5] = (Len>>8) & 0xFF
	SendData[6] = Len & 0xFF

	local offset = 7
	for k=1,ParamLen do
		SendData[offset] = string.byte(Param,k)
		offset = offset + 1
	end

	pBuf[0] = 0x7E
	DataLen = ParamLen+6
	HexToAscii(SendData, pBuf, DataLen, 1 )
	Length = DataLen*2

	local DataChecksum = 0
	for k=1,Length do
		DataChecksum = DataChecksum + pBuf[k]
	end
	DataChecksum = (~DataChecksum + 1) & 0xFFFF

	ConvertBuf[1] = (DataChecksum>>8) & 0xFF
	ConvertBuf[2] = DataChecksum & 0xFF
	HexToAscii(ConvertBuf, ChecksumBuf, 2, 1 )

	Checksumlen1 =  13 + ParamLen*2
	Checksumlen2 =  14 + ParamLen*2
	Checksumlen3 =  15 + ParamLen*2
	Checksumlen4 =  16 + ParamLen*2
	pBuf[Checksumlen1] = ChecksumBuf[1]
	pBuf[Checksumlen2] = ChecksumBuf[2]
	pBuf[Checksumlen3] = ChecksumBuf[3]
	pBuf[Checksumlen4] = ChecksumBuf[4]

	Endlen =  17 + ParamLen*2
	pBuf[Endlen] = 0x0D

	local sendpack=""
	pBufLength = 18 + ParamLen*2

	for k=1,pBufLength do
		sendpack = sendpack..string.char(pBuf[k-1])
	end

	return sendpack
end
function YDT1363_depack( Package )						-- 电总协议解包
	local DataVal={}
	DataLen = string.len(Package)
	for k=1,DataLen do
		Data = string.sub(Package,k,k)
		DataVal[k] = string.byte(Data)
	end

	if( DataVal[1] ~= 0x7E ) then return nil,1 end		--协议头校验错误
	ChecksumLen = string.sub(Package,10,13)
	Len = tonumber(ChecksumLen,16)

--	CID2 = string.sub(Package,8,9)
--	if( tonumber(CID2,16) ~= 0x00 ) then return nil end		--CID2错误

	LenChecksum		= (Len & 0xF) + ((Len >> 4) & 0xF) + ((Len >> 8) & 0xF)
	LenChecksum		= LenChecksum % 16
	LenChecksum		= (~LenChecksum + 1) & 0xF
	if( LenChecksum ~= ((Len >> 12) & 0xF) ) then return nil,2 end	--长度校验位错误

	local Count = 12 + (Len & 0x0FFF)
	local DataChecksum = 0
	for k=1,Count do
		DataChecksum = DataChecksum + DataVal[k+1]
	end
	DataChecksum = (~DataChecksum + 1) & 0xFFFF

	CheckLen = 14 + (Len & 0x0FFF)
	Checksum = string.sub(Package,CheckLen,CheckLen+3)
	if( tonumber(Checksum,16) ~= DataChecksum ) then return nil,3 end  --和校验错误

	retval = Len & 0x0FFF
	local rest = string.sub(Package,14,retval+13)
	local DataPack = ""
	local Offset = 1
	local ret = retval//2
	for k=1,ret do
		RestPack = string.sub(rest,Offset,Offset+1)
		Offset = Offset + 2
		if( RestPack =="  " ) then
			RestPack = "00"
		end
		Pack = tonumber(RestPack,16)
		CharData = string.char(Pack)
		DataPack = DataPack..CharData
	end
	return DataPack,0
end

-- Lua模版结束

