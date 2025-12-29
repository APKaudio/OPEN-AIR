
Public Module Switcher_HP3235




    Public CoaxSwitch As BenchInstrumentItem

    Public Sub Coax_Switch_setup()
        CoaxSwitch = New BenchInstrumentItem
		CoaxSwitch.Name = "Coax Switch"

		CoaxSwitch.Address.GPIB_Address = 10
		CoaxSwitch.Address.IP = "192.168.0.106"
		CoaxSwitch.Address.GPIB_Bus = "gpib7"


		CoaxSwitch.ConnectToGPIB()
    End Sub

End Module





'Public Module Switcher_HP3235
'    'This module is to control the Agilent 33401 SWR over GPIB bussing

'    Public SWRMgr As Ivi.Visa.Interop.ResourceManager


'    Public Structure HP3235Switcher
'        Dim Name As String ' This is the name of the device or the measurement you are taking
'        Dim Mode As Integer  ' what type of measurement are you taking
'        Dim SCIP As Ivi.Visa.Interop.FormattedIO488 ' the format of the ooperationg for control
'        Dim GPIBaddress As Integer ' from configuration menue CDec(UserInterface.SWR_gpibaddress_1.Text)


'        Dim NextState As String
'        Dim CurrentState As String
'        Dim Relay() As Boolean


'    End Structure

'    Public CoaxSwitch(4) As String ' row counter and status



'    Public SwitcherModule As HP3235Switcher



'    Public Sub SWRaddress()
'        CommandList("SWRaddress()")

'        SWRMgr = New Ivi.Visa.Interop.ResourceManager


'        Try
'            SwitcherModule.SCIP = New Ivi.Visa.Interop.FormattedIO488
'            SwitcherModule.SCIP.IO = SWRMgr.Open(("TCPIP0::" & UserInterface.GPIB_IP.Text & "::" & UserInterface.GPIB_BUSS.Text & "," & UserInterface.SWR_GPIB_ADDRESS.Text & "::INSTR"))    ' 10 is the instr. address 
'        Catch ex As Exception

'        End Try

'    End Sub




'    Public Sub COAX_SWR_CONNECT(ConnectROW As Int16, ConnectCOL As Integer, ROW As String)


'        Try

'            SwitcherModule.SCIP.WriteString("DISCONN " & CoaxSwitch(ROW))
'                CommandList("DISCONN " & CoaxSwitch(ROW))


'            SwitcherModule.SCIP.WriteString("CONNECT " & ConnectROW & "," & ConnectCOL)
'            CommandList("CONNECT " & ConnectROW & "," & ConnectCOL)
'            CoaxSwitch(ROW) = ConnectROW & "," & ConnectCOL
'        Catch ex As Exception
'            CommandList("SWR_Change:ERROR")
'        End Try
'    End Sub






'    Public Sub SWR_OUTPUT_BUS(ConnectROW As Int16, ConnectBUS As Integer)

'        Try
'            SwitcherModule.SCIP.WriteString("CONNECT " & ConnectROW & ", AB" & ConnectBUS)
'            CommandList("CONNECT " & ConnectROW & ", AB" & ConnectBUS)

'        Catch ex As Exception
'            CommandList("SWR_OUTPUT_BUS:ERROR")
'        End Try
'    End Sub






'    Public Sub SelectChannel(ConnectROW As Int16, ConnectBUS As Integer)

'        Try
'            '        SwitcherModule(9).SCIP.WriteString("Select " & ConnectROW)
'            SwitcherModule.SCIP.WriteString("Connect " & ConnectROW & ", AB" & ConnectBUS)
'            CommandList("Connect " & ConnectROW & ", AB" & ConnectBUS)

'        Catch ex As Exception
'            CommandList("SWR_OUTPUT_BUS:ERROR")
'        End Try
'    End Sub


'End Module



''Public Sub SWR_Change(Bank As Integer, Channel As Integer)
''    CommandList("SWR_Change(" & Bank & "," & Channel)

''    Dim channelwithzero As String

''    If Channel < 10 Then
''        channelwithzero = "0" & Channel
''    Else channelwithzero = Channel

''    End If

''    SwitcherModule(Bank).NextState = Bank & channelwithzero

''    If SwitcherModule(Bank).CurrentState <> SwitcherModule(Bank).NextState Then
''        Try
''            SwitcherModule(Bank).SCIP.WriteString("OPEN " & SwitcherModule(Bank).CurrentState)
''            CommandList("SWR_ChangeWRTIE : " & "OPEN " & SwitcherModule(Bank).CurrentState)

''            SwitcherModule(Bank).SCIP.WriteString("CLOSE " & SwitcherModule(Bank).NextState)
''            CommandList("SWR_ChangeWRTIE : " & "CLOSE " & SwitcherModule(Bank).NextState)

''            SwitcherModule(Bank).CurrentState = SwitcherModule(Bank).NextState
''        Catch ex As Exception
''            CommandList("SWR_Change:ERROR")
''        End Try
''    End If

''End Sub


''Public Sub SWR_Change_Channel(Bank As Integer, Channel As Integer)
''    CommandList("SWR_Change_Channel(" & Bank & "," & Channel)

''    SwitcherModule(Bank).NextState = Bank & ChannelToRelayLookup(Channel) & ChannelToRelayLookup(Channel)

''    Try
''        SwitcherModule(Bank).SCIP.WriteString("OPEN " & SwitcherModule(Bank).CurrentState)
''        CommandList("SWR_ChangeWRTIE : " & "OPEN " & SwitcherModule(Bank).CurrentState)

''        SwitcherModule(Bank).SCIP.WriteString("CLOSE " & SwitcherModule(Bank).NextState)
''        CommandList("SWR_ChangeWRTIE : " & "CLOSE " & SwitcherModule(Bank).NextState)

''        SwitcherModule(Bank).CurrentState = SwitcherModule(Bank).NextState
''    Catch ex As Exception
''        CommandList("SWR_Change:ERROR")
''        End Try

''End Sub


''Public Sub SWR_open(Bank As Integer, Channel As Integer)
''    CommandList("SWR_open(" & Bank & "," & Channel)

''    Dim channelwithzero As String

''    If Channel < 10 Then
''        channelwithzero = "0" & Channel
''    Else
''        channelwithzero = Channel
''    End If

''    SwitcherModule(Bank).NextState = Bank & channelwithzero

''    Try
''        SwitcherModule(Bank).SCIP.WriteString("OPEN " & SwitcherModule(Bank).NextState)
''        CommandList("SWR_ChangeWRTIE : " & "OPEN " & SwitcherModule(Bank).NextState)

''        SwitcherModule(Bank).CurrentState = SwitcherModule(Bank).NextState
''    Catch ex As Exception
''        CommandList("SWR_Change:ERROR")
''    End Try


''End Sub


''Public Sub SWR_CLOSE(Bank As Integer, Channel As Integer)
''    CommandList("SWR_CLOSE(" & Bank & "," & Channel)

''    Dim channelwithzero As String

''    If Channel < 10 Then
''        channelwithzero = "0" & Channel
''    Else
''        channelwithzero = Channel
''    End If

''    SwitcherModule(Bank).NextState = Bank & channelwithzero

''    Try
''        SwitcherModule(Bank).SCIP.WriteString("CLOSE " & SwitcherModule(Bank).NextState)
''        CommandList("SWR_ChangeWRTIE : " & "CLOSE " & SwitcherModule(Bank).NextState)

''        SwitcherModule(Bank).CurrentState = SwitcherModule(Bank).NextState
''    Catch ex As Exception
''        CommandList("SWR_Change:ERROR")
''    End Try
''End Sub