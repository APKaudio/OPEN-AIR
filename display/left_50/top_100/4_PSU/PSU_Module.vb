Public Class PSU_Module

    Private Received_Voltage As Double
    Private Received_Current As Double

	Private Module_Max_Voltage As Double
    Private Module_Max_Current As Double
    Private OutputEnabled_State As Boolean


	Public firstsupply As Integer = 0
	Public Lastsupply As Integer = 7


	Public DEVICE As BenchInstrumentItem







	'Public Sub ShutOffAllPSU()
	'	For moduletoshutoff As Integer = firstsupply To Lastsupply
	'		Try
	'			Ouput Off And Display OFF
	'			PSU_Frame.PSU(moduletoshutoff).Say("OUTPUT OFF;DISP:STAT 0")
	'			PSU_Frame.PSU(moduletoshutoff).Output = False

	'		Catch ex As Exception

	'		End Try

	'	Next
	'End Sub



	'Public Sub DisconnectAllPSU()
	'	For moduletoshutoff As Integer = firstsupply To Lastsupply
	'		Try
	'			Ouput Off And Display OFF
	'			PSU_Frame.PSU(moduletoshutoff).Say("OUTPUT OFF;DISP:STAT 0")
	'			PSU_Frame.PSU(moduletoshutoff).Output = False
	'		Catch ex As Exception

	'		End Try
	'		PSU_Frame.PSU(moduletoshutoff).Connected = False

	'	Next
	'End Sub




	Dim channel As Integer
	Public Property AES70_Property_Channel() As Integer
		Get
			Return channel
		End Get
		Set(ByVal value As Integer)
			channel = value
		End Set
	End Property


	Dim GPIB_Address As Integer
	Public Property AES70_Manager_GPIB_address() As Integer
		Get
			Return GPIB_Address
		End Get
		Set(ByVal value As Integer)
			GPIB_Address = value

		End Set
	End Property

	Dim GPIB_Bus As String
	Public Property AES70_Manager_GPIB_bus() As Integer
		Get
			Return GPIB_Bus
		End Get
		Set(ByVal value As Integer)
			GPIB_Bus = value

		End Set
	End Property


	Dim IPaddress As String
	Public Property AES70_Manager_IP_address() As String
		Get
			Return IPaddress
		End Get
		Set(ByVal value As String)
			IPaddress = value

		End Set
	End Property



	Dim RouterConnection As Integer
	Public Property AES70_Property_ChangeRouterConnection() As Integer
		Get
			Return RouterConnection
		End Get
		Set(ByVal value As Integer)
			RouterConnection = value

		End Set
	End Property



	Public Property DataReadVoltage() As Double
        Get
            Return Received_Voltage

        End Get
        Set(value As Double)
            Received_Voltage = value
            Display_Voltage.Value_To_Display = Received_Voltage

        End Set
    End Property


    Public Property DataReadCurrent() As Double
        Get
            Return Received_Current
        End Get
        Set(value As Double)
            Received_Current = value
            Display_Current.Value_To_Display = Received_Current
        End Set
    End Property



	Public Property ModuleMaxVoltage() As String
        Get
            Return Module_Max_Voltage
        End Get
		Set(value As String)
			Module_Max_Voltage = value
			PSU_Vset.Text = Module_Max_Voltage
		End Set
	End Property

	Public Property AES70_ModuleMaxCurrent() As String
		Get
			Return Module_Max_Current
		End Get
		Set(value As String)
			Module_Max_Current = value
			PSU_Iset.Text = Module_Max_Current

		End Set
	End Property


	Public Property AES70_OutputEnabled() As Boolean

		Get
			Return AES70_OutputEnabled
		End Get
		Set(value As Boolean)
			OutputEnabled_State = value
			'PSU_Iset.Text = Module_Max_Current

		End Set
	End Property



	Public Sub SetConfiguration()

		DataReadVoltage = DEVICE.Max.VDC / 2

		'Change Imax set to 1/2 maximum current

		'set Voltage to 1/2 maximum power
		DataReadCurrent = DEVICE.Max.IDC / 2

		Set_Output_Level_Max()

	End Sub


	Public Sub PSU_Frame_Output()


		'GET OUTPUT STATUS
		Try
			DEVICE.Say("OUTPUT?")
			DEVICE.Output = DEVICE.Listen()

		Catch ex As Exception

		End Try


		If DEVICE.Output Then 'module is on
			'Turn Module OFF
			DEVICE.Say("OUTPUT OFF;DISP:STAT 0")

		Else
			'module is off
			SetConfiguration()
			DEVICE.Say("OUTPUT ON;DISP:STAT 1")
		End If

		'check status
		DEVICE.Say("OUTPUT?")
		DEVICE.Output = DEVICE.Listen()



		If DEVICE.Output Then
			Button_PSU_OutputEnable.BackColor = ChangeNumbertoColor(DEVICE.Address.Channel + 1)
			Button_PSU_OutputEnable.ForeColor = Color.Black
			Button_PSU_OutputEnable.Text = "ON"

			Display_Voltage.Visible = True
			Display_Current.Visible = True
			Display_Power.Visible = True

			Label_Current.Visible = False
			Label_Voltage.Visible = False

		Else
			Button_PSU_OutputEnable.BackColor = Color.DarkSlateGray
			Button_PSU_OutputEnable.ForeColor = Color.White
			Button_PSU_OutputEnable.Text = "OFF"

			Display_Voltage.Visible = False
			Display_Current.Visible = False
			Display_Power.Visible = False

			Label_Current.Visible = True
			Label_Voltage.Visible = True


		End If




	End Sub



	Public Sub Set_Output_Level_Max()
		If DEVICE.Connected Then

			DEVICE.Configuration.VDC = PSU_Vset.Text
			DEVICE.Configuration.IDC = PSU_Iset.Text

			Try
				DEVICE.Say("VOLT:LEVEL " & DEVICE.Configuration.VDC)
				DEVICE.Say("CURR:LEVEL " & DEVICE.Configuration.IDC)
			Catch ex As Exception

			End Try
		End If

	End Sub









	Public Sub ReadVoltage()
		'Set command to read Voltage
		Try

			If DEVICE.Connected And DEVICE.Output Then
				DEVICE.Say("MEAS:VOLT?")
				DEVICE.Read.VDC = DEVICE.Listen()
			Else
			End If
			'UPDATE DISPLAY
			Display_Voltage.Value_To_Display = DEVICE.Read.VDC
		Catch ex As Exception
			ErrorList(System.Reflection.MethodBase.GetCurrentMethod.Name)
			Display_Voltage.Value_To_Display = 0

		End Try

	End Sub


	Public Sub ReadCurrent()


		'Set command to read Voltage
		Try
			If DEVICE.Connected And DEVICE.Output Then
				DEVICE.Say("MEAS:CURR?")
				DEVICE.Read.IDC = DEVICE.Listen()
				Display_Current.Value_To_Display = DEVICE.Read.IDC
			End If

		Catch ex As Exception
			ErrorList(System.Reflection.MethodBase.GetCurrentMethod.Name)
			Display_Current.Value_To_Display = 0
		End Try




	End Sub


	Public Sub ReadPower()
		ReadCurrent()
		ReadVoltage()

		DEVICE.Read.Power = DEVICE.Read.IDC * DEVICE.Read.VDC
		Display_Power.Value_To_Display = DEVICE.Read.Power

	End Sub




	Private Sub PSU_OutputEnable_7_Click(sender As Object, e As EventArgs) Handles Button_PSU_OutputEnable.Click
		PSU_Frame_Output()
	End Sub



	Private Sub PSU_Vset_TextChanged(sender As Object, e As EventArgs) Handles PSU_Vset.Leave
		Set_Output_Level_Max()
	End Sub

	Private Sub PSU_Iset_TextChanged(sender As Object, e As EventArgs) Handles PSU_Iset.Leave
		Set_Output_Level_Max()
	End Sub

	Private Sub PSU_Module_Load_1(sender As Object, e As EventArgs) Handles MyBase.Load

		If SequenceTimer.Visible Then
			Try
				PSU_frame_setup()
				'End If

				Button_PSU_OutputEnable.BackColor = ChangeNumbertoColor(DEVICE.Address.Channel + 1)
				PSU_Vset.BackColor = ChangeNumbertoColor(DEVICE.Address.Channel + 1)
				PSU_Iset.BackColor = ChangeNumbertoColor(DEVICE.Address.Channel + 1)

				Display_Voltage.ModuleNumber = (DEVICE.Address.Channel + 1)
				Display_Current.ModuleNumber = (DEVICE.Address.Channel + 1)
				Display_Power.ModuleNumber = (DEVICE.Address.Channel + 1)
			Catch ex As Exception
				'Me.Dispose()
				Me.Visible = False
			End Try
			'If Me.Visible = True Then

		End If

	End Sub

	Private Sub PSUCLOSE() Handles Me.Disposed

		Try
			DEVICE.Say("OUTPUT OFF;DISP:STAT 0")
		Catch ex As Exception

		End Try

	End Sub

	Private Sub Display_Power_mouseHover(sender As Object, e As EventArgs) Handles Display_Current.MouseHover, Display_Voltage.MouseHover, Display_Power.MouseHover
		'Me.Size = New Size(500, 500)
	End Sub

	Private Sub Display_Power_mouseleave(sender As Object, e As EventArgs) Handles Display_Current.MouseMove, Display_Voltage.MouseMove, Display_Power.MouseMove
		'Me.Size = New Size(200, 110)
	End Sub




	Public Sub PSU_frame_setup()


		Try
			'Create new instance of bench item
			DEVICE = New BenchInstrumentItem
			DEVICE.Name = "PSU " & channel
			DEVICE.Address.GPIB_Address = GPIB_Address
			DEVICE.Address.IP = IPaddress
			DEVICE.Address.GPIB_Bus = "gpib" & GPIB_Bus
			DEVICE.Address.Channel = channel
			DEVICE.Matrix.Port = RouterConnection

			'adds the sub module to the GPIB address
			DEVICE.Address.GPIB_Address = DEVICE.Address.GPIB_Address & "," & channel

			'Connect device

			DEVICE.ConnectToGPIB()

			'expected IDN
			DEVICE.GetDeviceIDN()

			'Get Max voltage And current based on the IDN results
			PSUFrame_Get_ModuleMaxVoltageandCurrent(DEVICE)

		Catch ex As Exception

			'Me.Dispose()
			Me.Visible = False

		End Try



	End Sub




	Public Sub PSUFrame_Get_ModuleMaxVoltageandCurrent(ModuleBeingAddressed As BenchInstrumentItem)
		If ModuleBeingAddressed.Connected Then
			'The module model installed at the frame is returned.  at the 21st character position is the unit model number]
			'the below lookups are the maximum voltage and current rating of the corresponding modules
			Dim PositionOfModuleDesignation As Integer = 21
			Dim moduletypeextracted = Mid(ModuleBeingAddressed.Address.IDN, PositionOfModuleDesignation, 1)

			'FIND MAX AND MIN VOLTAGE AND CURRENT BASED ON WHAT MODULE IS IN THE FRAME
			Select Case moduletypeextracted
				Case 1
					'66101
					ModuleBeingAddressed.Max.VDC = 8
					ModuleBeingAddressed.Max.IDC = 16
				Case 2
					'66102
					ModuleBeingAddressed.Max.VDC = 20
					ModuleBeingAddressed.Max.IDC = 7.5
				Case 4

					'66104
					ModuleBeingAddressed.Max.VDC = 60
					ModuleBeingAddressed.Max.IDC = 2.5
			End Select
			'CALCULATE MAXIMUM POWER BASED ON THE COLLECTED DATA
			ModuleBeingAddressed.Max.Power = ModuleBeingAddressed.Max.IDC * ModuleBeingAddressed.Max.VDC
		End If


	End Sub

	Private Sub Display_Power_Load(sender As Object, e As EventArgs) Handles Display_Power.Load

	End Sub

	Private Sub Display_Voltage_Load(sender As Object, e As EventArgs) Handles Display_Voltage.Load

	End Sub
End Class
