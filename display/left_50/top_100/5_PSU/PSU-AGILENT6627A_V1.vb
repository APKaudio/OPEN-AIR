Module PSU_AGILENT6627A_V1

    '  Public PSU As Ivi.Visa.Interop.FormattedIO488
    Public PSUioMgr As Ivi.Visa.Interop.ResourceManager

    Public Structure PowerSupply
        Dim Connected As Boolean

        Dim Status As Boolean ' ON or OFF
        Dim Link As Integer ' the channel it is linked to

        'Controls
        Dim SendVoltage As Double ' The Voltage sent to the PSU
        Dim SendCurrentLimit As Double ' the current limit of 

        'Recieve 
        Dim ReadVoltage As Double ' the voltage read by the PSU
        Dim ReadCurrent As Double ' the Current of the PSU

        Dim CalcPower As Double ' Calculated Power

        Dim SCIP As Ivi.Visa.Interop.FormattedIO488
    End Structure

    Public PSU_CH(4) As PowerSupply



    Public Sub PSUAssignAddress(Channel As Integer)
        Try
            CommandList("PSUAssignAddress-" & Channel)
            PSUioMgr = New Ivi.Visa.Interop.ResourceManager

            PSU_CH(Channel).SCIP = New Ivi.Visa.Interop.FormattedIO488
            PSU_CH(Channel).SCIP.IO = PSUioMgr.Open(("TCPIP0::" & UserInterfaceShell.GPIB_IP.Text & "::" & UserInterfaceShell.GPIB_BUSS.Text & "," & UserInterfaceShell.PSU_GPIB_ADDRESS.Text & "::INSTR"))    ' 10 is the instr. address 

            PSU_CH(Channel).Connected = True
        Catch ex As Exception
            PSU_CH(Channel).Connected = False

        End Try

    End Sub

    Public Sub PSU_Update(Channel As Integer)
        If PSU_CH(Channel).Connected = True Then

            Try
                CommandList("PSU_Update-" & Channel)
                PSU_CH(Channel).SCIP.WriteString("VSET " & Channel & "," & PSU_CH(Channel).SendVoltage)
                PSU_CH(Channel).SCIP.WriteString("ISET " & Channel & "," & PSU_CH(Channel).SendCurrentLimit)

            Catch ex As Exception
                CommandList("ERROR: PSU_Update-" & Channel)
                PSU_CH(Channel).Connected = False
            End Try
        End If

    End Sub


    Public Sub PSU_Status(Channel As Integer, Status As Boolean)
        If PSU_CH(Channel).Connected = True Then

            If Status = True Then
                Try
                    CommandList("PSU_Status-" & Channel & " ON")
                    PSU_CH(Channel).SCIP.WriteString("OUT " & Channel & ",1")
                    PSU_CH(Channel).Status = True
                Catch ex As Exception
                    CommandList("ERROR: PSU_Status-" & Channel)
                    PSU_CH(Channel).Connected = False
                End Try

            Else
                Try
                    CommandList("PSU_Status-" & Channel & " OFF")
                    PSU_CH(Channel).SCIP.WriteString("OUT " & Channel & ",0")
                    PSU_CH(Channel).Status = False
                Catch ex As Exception
                    CommandList("ERROR: PSU_Status-" & Channel)
                    PSU_CH(Channel).Connected = False
                End Try

            End If
        End If
    End Sub


    Public Sub ReadPSUValue(Channel As Integer)
        If PSU_CH(Channel).Connected = True Then

            'REad voltage and current
            Try
                CommandList("ReadPSUValue-" & Channel)

                PSU_CH(Channel).SCIP.WriteString("VOUT? " & Channel)
                PSU_CH(Channel).ReadVoltage = PSU_CH(Channel).SCIP.ReadString

                PSU_CH(Channel).SCIP.WriteString("IOUT? " & Channel)
                PSU_CH(Channel).ReadCurrent = PSU_CH(Channel).SCIP.ReadString

                PSU_CH(Channel).CalcPower = PSU_CH(Channel).ReadVoltage * PSU_CH(Channel).ReadCurrent


                Dim PSUupdateCurrent() As Control = UserInterfaceShell.Controls.Find("PSU_READ_I_" & Channel, 1)
                PSUupdateCurrent(0).Text = PSU_CH(Channel).ReadCurrent

                Dim PSUupdateVoltage() As Control = UserInterfaceShell.Controls.Find("PSU_READ_V_" & Channel, 1)
                PSUupdateVoltage(0).Text = PSU_CH(Channel).ReadVoltage

                Dim PSUupdateCalcapower() As Control = UserInterfaceShell.Controls.Find("PSU_POWER_CALC_" & Channel, 1)
                PSUupdateCalcapower(0).Text = PSU_CH(Channel).CalcPower


            Catch ex As Exception
                CommandList("ERROR: " & "ReadPSUValue-" & Channel)
                PSU_CH(Channel).Connected = False
            End Try
        End If
    End Sub

    Sub PSU_Off(Channel)
        PSU_Status(Channel, 0)
    End Sub

    '    Private Sub Button_PSU_STATE_1(sender As Object, e As EventArgs) Handles PSU_ON_1.Click

    '        If PSU_ON_1.Text = "ON" Then
    '            PSU.WriteString("VSET 1," & PSU_V_1.Text)
    '            PSU.WriteString("ISET 1," & PSU_I_1.Text)
    '            PSU.WriteString("OUT 1,1")
    '            PSU_ON_1.Text = "OFF"
    '            PSU_ON_1.BackColor = Color.Orange
    '        ElseIf PSU_ON_1.Text = "OFF" Then
    '            PSU.WriteString("OUT 1,0")
    '            PSU_ON_1.Text = "ON"
    '            PSU_ON_1.BackColor = Color.Transparent
    '        End If
    '        If PSULink12.Checked Then
    '            If PSU_ON_2.Text = "ON" Then
    '                PSU_V_2.Text = PSU_V_1.Text
    '                PSU_I_2.Text = PSU_I_1.Text
    '                PSU.WriteString("VSET 2," & PSU_V_1.Text)
    '                PSU.WriteString("ISET 2," & PSU_I_1.Text)
    '                PSU.WriteString("OUT 2,1")
    '                PSU_ON_2.Text = "OFF"
    '                PSU_ON_2.BackColor = Color.Orange
    '            ElseIf PSU_ON_2.Text = "OFF" Then
    '                PSU.WriteString("OUT 2,0")
    '                PSU_ON_2.Text = "ON"
    '                PSU_ON_2.BackColor = Color.Transparent
    '            End If

    '        End If

    '        ReadPSUValue()

    '    End Sub
    '    Private Sub BButton_PSU_STATE_3(sender As Object, e As EventArgs) Handles PSU_ON_2.Click
    '        If PSU_ON_2.Text = "ON" Then
    '            PSU.WriteString("VSET 2," & PSU_V_2.Text)
    '            PSU.WriteString("ISET 2," & PSU_I_2.Text)
    '            PSU.WriteString("OUT 2,1")
    '            PSU_ON_2.Text = "OFF"
    '            PSU_ON_2.BackColor = Color.Orange
    '        ElseIf PSU_ON_2.Text = "OFF" Then
    '            PSU.WriteString("OUT 2,0")
    '            PSU_ON_2.Text = "ON"
    '            PSU_ON_2.BackColor = Color.Transparent
    '        End If




    '        ReadPSUValue()
    '    End Sub
    '    Private Sub Button_PSU_STATE_3(sender As Object, e As EventArgs) Handles PSU_ON_3.Click

    '        If PSU_ON_3.Text = "ON" Then
    '            PSU.WriteString("VSET 3," & PSU_V_3.Text)
    '            PSU.WriteString("ISET 3," & PSU_I_3.Text)
    '            PSU.WriteString("OUT 3,1")
    '            PSU_ON_3.Text = "OFF"
    '            PSU_ON_3.BackColor = Color.Orange

    '        ElseIf PSU_ON_3.Text = "OFF" Then
    '            PSU.WriteString("OUT 3,0")
    '            PSU_ON_3.Text = "ON"
    '            PSU_ON_3.BackColor = Color.Transparent
    '        End If

    '        If PSULINK34.Checked Then
    '            PSU_V_4.Text = PSU_V_3.Text
    '            PSU_I_4.Text = PSU_I_3.Text
    '            If PSU_ON_4.Text = "ON" Then
    '                PSU.WriteString("VSET 4," & PSU_V_3.Text)
    '                PSU.WriteString("ISET 4," & PSU_I_3.Text)
    '                PSU.WriteString("OUT 4,1")
    '                PSU_ON_4.Text = "OFF"
    '                PSU_ON_4.BackColor = Color.Orange
    '            ElseIf PSU_ON_4.Text = "OFF" Then
    '                PSU.WriteString("OUT 4,0")
    '                PSU_ON_4.Text = "ON"
    '                PSU_ON_4.BackColor = Color.Transparent
    '            End If


    '        End If

    '        ReadPSUValue()
    '    End Sub
    '    Private Sub Button_PSU_STATE_4(sender As Object, e As EventArgs) Handles PSU_ON_4.Click
    '        If PSU_ON_4.Text = "ON" Then
    '            PSU.WriteString("VSET 4," & PSU_V_4.Text)
    '            PSU.WriteString("ISET 4," & PSU_I_4.Text)
    '            PSU.WriteString("OUT 4,1")
    '            PSU_ON_4.Text = "OFF"
    '            PSU_ON_4.BackColor = Color.Orange
    '        ElseIf PSU_ON_4.Text = "OFF" Then
    '            PSU.WriteString("OUT 4,0")
    '            PSU_ON_4.Text = "ON"
    '            PSU_ON_4.BackColor = Color.Transparent
    '        End If
    '        ReadPSUValue()
    '    End Sub

    '    Private Sub BUTTON_PSU_OFF(sender As Object, e As EventArgs) Handles Button2.Click

    '        PSUOFF()


    '    End Sub

    '    Public Sub PSUOFF()
    '        If PSU_Enable.Checked = True Then
    '            PSU.WriteString("OUT 1,0")

    '            PSU_ON_1.Text = "ON"
    '            PSU_ON_1.BackColor = Color.Transparent

    '            PSU.WriteString("OUT 2,0")
    '            PSU_ON_2.Text = "ON"
    '            PSU_ON_2.BackColor = Color.Transparent

    '            PSU.WriteString("OUT 3,0")
    '            PSU_ON_3.Text = "ON"
    '            PSU_ON_3.BackColor = Color.Transparent

    '            PSU.WriteString("OUT 4,0")
    '            PSU_ON_4.Text = "ON"
    '            PSU_ON_4.BackColor = Color.Transparent

    '            ReadPSUValue()
    '        End If
    '    End Sub


    '    Public Sub ReadPSUValue()

    '        If PSU_Enable.Checked = True Then
    '            ReadPSUValue_1()
    '            ReadPSUValue_2()
    '            ReadPSUValue_3()
    '            ReadPSUValue_4()
    '        End If

    '    End Sub
    '    Public Sub ReadPSUValue_1()
    '        'REad voltage and current
    '        PSU.WriteString("VOUT? 1")
    '        PSU_READ_V_1.Text = PSU.ReadString
    '        PSU.WriteString("IOUT? 1")
    '        PSU_READ_I_1.Text = PSU.ReadString
    '    End Sub
    '    Public Sub ReadPSUValue_2()
    '        'REad voltage and current
    '        PSU.WriteString("VOUT? 2")
    '        PSU_READ_V_2.Text = PSU.ReadString
    '        PSU.WriteString("IOUT? 2")
    '        PSU_READ_I_2.Text = PSU.ReadString
    '    End Sub

    '    Public Sub ReadPSUValue_4()
    '        'REad voltage and current
    '        PSU.WriteString("VOUT? 4")
    '        PSU_READ_V_4.Text = PSU.ReadString
    '        PSU.WriteString("IOUT? 4")
    '        PSU_READ_I_4.Text = PSU.ReadString
    '    End Sub


    '    Private Sub PSU LINKCheckBox2_CheckedChanged(sender As Object, e As EventArgs) Handles PSULink12.CheckedChanged
    '        PSU.WriteString("OUT 1,0")
    '        PSU_ON_1.Text = "ON"
    '        PSU_ON_1.BackColor = Color.Transparent

    '        PSU.WriteString("OUT 2,0")
    '        PSU_ON_2.Text = "ON"
    '        PSU_ON_2.BackColor = Color.Transparent

    '        PSU_V_2.Enabled = Not PSU_V_2.Enabled
    '        PSU_I_2.Enabled = Not PSU_I_2.Enabled
    '        PSU_ON_2.Enabled = Not PSU_ON_2.Enabled

    '    End Sub

    '    Private Sub PSULINK34(sender As Object, e As EventArgs) Handles PSULINK34.CheckedChanged
    '        PSU.WriteString("OUT 3,0")
    '        PSU_ON_3.Text = "ON"
    '        PSU_ON_3.BackColor = Color.Transparent
    '        PSU.WriteString("OUT 4,0")
    '        PSU_ON_4.Text = "ON"
    '        PSU_ON_4.BackColor = Color.Transparent

    '        PSU_V_4.Enabled = Not PSU_V_4.Enabled
    '        PSU_I_4.Enabled = Not PSU_I_4.Enabled
    '        PSU_ON_4.Enabled = Not PSU_ON_4.Enabled
    '    End Sub




    '    Private Sub PSU_READ_V_1_TextChanged_1(sender As Object, e As EventArgs) Handles PSU_READ_V_1.DoubleClick
    '        ReadPSUValue_1()
    '        My.Computer.Clipboard.SetText(PSU_READ_V_1.Text)
    '    End Sub

    '    Private Sub PSU_READ_V_2_TextChanged_1(sender As Object, e As EventArgs) Handles PSU_READ_V_2.DoubleClick
    '        ReadPSUValue_2()
    '        My.Computer.Clipboard.SetText(PSU_READ_V_2.Text)
    '    End Sub

    '    Private Sub PSU_READ_V_3_TextChanged_1(sender As Object, e As EventArgs) Handles PSU_READ_V_3.DoubleClick
    '        ReadPSUValue_3()
    '        My.Computer.Clipboard.SetText(PSU_READ_V_3.Text)
    '    End Sub
    '    Private Sub PSU_READ_V_4_TextChanged_1(sender As Object, e As EventArgs) Handles PSU_READ_V_4.DoubleClick
    '        ReadPSUValue_4()
    '        My.Computer.Clipboard.SetText(PSU_READ_V_4.Text)
    '    End Sub

    '    Private Sub PSU_READ_I_1_TextChanged(sender As Object, e As EventArgs) Handles PSU_READ_I_1.DoubleClick
    '        ReadPSUValue_1()
    '        My.Computer.Clipboard.SetText(PSU_READ_I_1.Text)
    '    End Sub


    '    Private Sub PSU_READ_I_2_TextChanged(sender As Object, e As EventArgs) Handles PSU_READ_I_2.DoubleClick
    '        ReadPSUValue_2()
    '        My.Computer.Clipboard.SetText(PSU_READ_I_2.Text)
    '    End Sub


    '    Private Sub PSU_READ_I_3_TextChanged(sender As Object, e As EventArgs) Handles PSU_READ_I_3.DoubleClick
    '        ReadPSUValue_3()
    '        My.Computer.Clipboard.SetText(PSU_READ_I_3.Text)
    '    End Sub


    '    Private Sub PSU_READ_I_4_TextChanged(sender As Object, e As EventArgs) Handles PSU_READ_I_4.DoubleClick
    '        ReadPSUValue_4()
    '        My.Computer.Clipboard.SetText(PSU_READ_I_4.Text)
    '    End Sub


End Module
