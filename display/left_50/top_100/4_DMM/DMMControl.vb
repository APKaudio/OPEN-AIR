Imports System.Threading

Public Class DMMControl

	Public DEVICE As BenchInstrumentItem

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

	Public MeterBeingAddressed As Integer
	Public Property Meter_to_Address() As Double
		Get
			Return MeterBeingAddressed
		End Get
		Set(ByVal value As Double)
			MeterBeingAddressed = value
			Horizontal_Meter.ModuleNumber = MeterBeingAddressed
			Vertical_Meter.ModuleNumber = MeterBeingAddressed
		End Set
	End Property

	Private Sub DMMControl_Load(sender As Object, e As EventArgs) Handles MyBase.Load

		If SequenceTimer.Visible Then
			SetupDMM(MeterBeingAddressed)
			Vertical_Meter.Location = New Point(0, 10)
			Horizontal_Meter.Height = Me.Height - 10
			Horizontal_Meter.Width = (Me.Width / 3) * 2

			Vertical_Meter.Location = New Point(Horizontal_Meter.Width, 0)
			Vertical_Meter.Width = Me.Width / 3
			Vertical_Meter.Height = Me.Height


			Me.BackColor = ChangeNumbertoColor(MeterBeingAddressed)
		End If

	End Sub

	Public Sub SetupDMM(ModuleBeingAddressed)
		DEVICE = New BenchInstrumentItem
		DEVICE.Name = "DMM " & ModuleBeingAddressed
		DEVICE.Address.GPIB_Address = GPIB_Address
		DEVICE.Address.IP = IPaddress
		DEVICE.Address.GPIB_Bus = "gpib" & GPIB_Bus
		DEVICE.Address.Channel = channel
		DEVICE.Matrix.Port = RouterConnection


		DEVICE.ConnectToGPIB()

		If DEVICE.Connected Then
			DEVICE.ChangeName("DMM " & ModuleBeingAddressed)
			DEVICE.GetDeviceIDN()
			Display_Values(ModuleBeingAddressed)
			ComboBox_DMM_function.SelectedIndex = 0
		Else
			'Me.Dispose()
			Me.Visible = False

		End If

	End Sub


	Public Sub ChangeMeterMode()
		If DEVICE.Connected Then
			DEVICE.Mode = ComboBox_DMM_function.Text
			DEVICE.ModeSCPI = MeterModeSCIP(DEVICE.Mode)
			DEVICE.Say(DEVICE.ModeSCPI)
		End If

	End Sub

	Public Function MeterModeSCIP(DMM_function As String) As String
		Dim SCIPcommandToConfig As String = ""
		'   Dim resolution As Double
		'   resolution = 1 / (10 ^ BenchDEVICE.TrackBar_Resolution.Value)
		Select Case DMM_function
			Case "V DC"
				SCIPcommandToConfig = "CONF:VOLT:DC 100,0.001"'  1," & resolution
				'SCIPcommandToConfig = "CONF:VOLT:DC 1,0.001"'  1," & resolution
		'1 I DC
			Case "I DC"
				SCIPcommandToConfig = "CONF:CURR:DC"
		'2 V AC
			Case "V AC"
				SCIPcommandToConfig = "CONF:VOLT:AC 10, 0.003"
		'3 I AC
			Case "A AC"
				SCIPcommandToConfig = "CONF:CURR:AC"
		'4 R 2W
			Case "R 2W"
				SCIPcommandToConfig = "CONF:RES"
		'5 R 4W
			Case "R 4W"
				SCIPcommandToConfig = "CONF:FRES"
		'6 Diode
			Case "Diode"
				SCIPcommandToConfig = "CONF:DIODe"
		'7 Capacitance
			Case "Capacitance"
				SCIPcommandToConfig = "CONF:FREQuency"
		'8 Freq
			Case "Freq"
				SCIPcommandToConfig = "CONF:FREQuency"
		'9 Period
			Case "Period"
				SCIPcommandToConfig = "CONF:PERiod"
		'10 Continuity
			Case "Continuity"
				SCIPcommandToConfig = "CONF:CONTinuity"
		End Select

		Return SCIPcommandToConfig

	End Function


	Public Sub ReadDMM()


		Try
			If DEVICE.Connected Then
				DEVICE.Say("READ?")
				DEVICE.Read.Raw = DEVICE.Listen()
				Store_Value(DEVICE.Read.Raw)
				If IsNumeric(DEVICE.Read.Raw) Then
					If DEVICE.Read.Raw > 2000000000000.0 Then
						'huge number 
						Display_Values(0)
					Else

						Display_Values(DEVICE.Read.Raw)
					End If
				End If



			Else
				ErrorList(System.Reflection.MethodBase.GetCurrentMethod.Name)
			End If
		Catch ex As Exception

		End Try

	End Sub

	Public Sub Store_Value(ValueReadOnDMM)
		If DEVICE.Connected Then
			DEVICE.Read.Raw = ValueReadOnDMM
			If IsNumeric(ValueReadOnDMM) Then
				Select Case DEVICE.Mode
					Case "V DC"
						DEVICE.Read.VDC = CDbl(ValueReadOnDMM)
					   '1 I DC
					Case "I DC"
						DEVICE.Read.IDC = CDbl(ValueReadOnDMM)
					 '2 V AC
					Case "V AC"

					Case "V AC"
						If IsNumeric(ValueReadOnDMM) Then
							DEVICE.Read.VAC = CDbl(ValueReadOnDMM)
						End If

						'3 I AC
					Case "A AC"
						DEVICE.Read.IAC = CDbl(ValueReadOnDMM)
						'4 R 2W
					Case "R 2W"
						DEVICE.Read.Resistance = CDbl(ValueReadOnDMM)
					  '5 R 4W
					Case "R 4W"
						DEVICE.Read.Resistance = CDbl(ValueReadOnDMM)
						'6 Diode
					Case "Diode"
						DEVICE.Read.Diode = CDbl(ValueReadOnDMM)
						'7 Capacitance
					Case "Capacitance"
						DEVICE.Read.Capacitance = CDbl(ValueReadOnDMM)
					   '8 Freq
					Case "Freq"
						DEVICE.Read.Freq = CDbl(ValueReadOnDMM)
						 '9 Period
					Case "Period"
						DEVICE.Read.Period = CDbl(ValueReadOnDMM)
					  '10 Continuity
					Case "Continuity"
						DEVICE.Read.Period = CDbl(ValueReadOnDMM)
				End Select
			End If
		End If

	End Sub

	Public Sub Display_Values(ValueReadOnDMM)
		If IsNumeric(ValueReadOnDMM) Then
			Horizontal_Meter.Value_To_Display = ValueReadOnDMM
			Vertical_Meter.Plot_V1 = ValueReadOnDMM
			MeasurementName.Text = DEVICE.Name
		Else
			Horizontal_Meter.Value_To_Display = 0
		End If
	End Sub


	Private Sub ComboBox_DMM_function_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ComboBox_DMM_function.SelectedIndexChanged
		If DEVICE.Connected Then
			ChangeMeterMode()
			ReadDMM()
		End If

	End Sub

	Private Sub MeasurementName_TextChanged(sender As Object, e As EventArgs) Handles MeasurementName.Leave
		DEVICE.Name = MeasurementName.Text
	End Sub

	Private Sub Vertical_Meter_Load(sender As Object, e As EventArgs) Handles Vertical_Meter.Load

	End Sub
End Class
