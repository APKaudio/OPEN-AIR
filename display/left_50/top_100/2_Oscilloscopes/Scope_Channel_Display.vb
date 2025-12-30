Imports System.Windows.Forms.DataVisualization.Charting

Public Class Scope_Channel_Display
	Public DEVICE As BenchInstrumentItem
	Private DataThatWillBeGraphed As String
	Public GraphDelayCount As Integer
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
			Button_RouteMe.Text = RouterConnection
		End Set
	End Property


	'Public Structure DifferenceBetweenChannel
	'	Dim DiffGaindBm As Double
	'	Public DiffPhase As Double
	'End Structure


	Private Sub UI_Scope_Channel_Display_Load(sender As Object, e As EventArgs) Handles MyBase.Load

		Scope_Channel_Display_Resize(sender, e)
		Config_AgilentScope(channel)

		'set instrument defaults

		ScopeAutoscale(channel)
		CheckBox_Vrms.Checked = True
		TrackBar_Horizontal.Value = 30


		Get_ScopeMeasureAll(channel)


	End Sub

	Private Sub Scope_Channel_Display_Resize(sender As Object, e As EventArgs) Handles MyBase.Resize
		TextBox_SCOPE_Title.Location = New Point(-5, -5)
		TableLayoutPanel_MAIN.Height = Me.Height
		TableLayoutPanel_MAIN.Width = Me.Width
		TableLayoutPanel_MAIN.Location = New Point(0, 0)
		display_VPP.ModuleNumber = channel
		display_Vrms.ModuleNumber = channel
		display_dBm.ModuleNumber = channel
		display_freq.ModuleNumber = channel
	End Sub





















	Public Sub Config_AgilentScope(channel)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			DEVICE = New BenchInstrumentItem
			DEVICE.Name = "Scope " & channel
			DEVICE.Address.GPIB_Address = GPIB_Address
			DEVICE.Address.IP = IPaddress
			DEVICE.Address.GPIB_Bus = "gpib" & GPIB_Bus
			DEVICE.Address.Channel = channel
			DEVICE.Matrix.Port = RouterConnection
			DEVICE.ConnectToGPIB()
			DEVICE.DeviceReset()

		Catch ex As Exception
			ErrorList("ERROR: Agilent_Scope_Form_Load FAIL")

		End Try
	End Sub

	Public Sub Get_ScopeMeasureAll(Channel)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		If DEVICE.Connected Then

			If GraphDelayCount >= TrackBar_GraphDelay.Value And CheckBox_graph.Checked Then
				plot(Channel)
				GraphDelayCount = 0
			End If
			GraphDelayCount = GraphDelayCount + 1

			If CheckBox_VPP.Checked Then
				ScopeMeasureVPP(Channel)
			End If

			If CheckBox_Vrms.Checked Then
				ScopeMeasureVrms(Channel)
				DisplayDBM(Channel)
			End If

			If CheckBox_freq.Checked Then
				Get_ScopeFreq(Channel)
			End If
		Else

		End If
	End Sub

	'Public Sub ScopeReadEverything(Channel)
	'	CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
	'	Get_ScopeMeasureAll(Channel)
	'End Sub






	'///////////////////////////////////////////////
	'BANDWIDTH
	Public Sub Set_ScopeBandwidthLimitChange(Channel As Integer, BandwidthLimit As Boolean)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If BandwidthLimit Then
				DEVICE.Say(":CHANnel" & Channel & ":BWLimit 20M")
			Else
				DEVICE.Say(":CHANnel" & Channel & ":BWLimit OFF")
			End If
		Catch ex As Exception

		End Try


	End Sub

	'///////////////////////////////////////////////
	'PROBE COUPLING
	Public Sub Set_ScopeChannelCoupling(Channel As Integer, CouplingMode As String)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		If CouplingMode = "AC" Then
			DEVICE.Say(":CHANnel" & Channel & ":COUPling AC")
		ElseIf CouplingMode = "DC" Then
			DEVICE.Say(":CHANnel" & Channel & ":COUPling DC")
		ElseIf CouplingMode = "GND" Then
			DEVICE.Say(":CHANnel" & Channel & ":COUPling GND")
		End If
	End Sub


	'///////////////////////////////////////////////
	'Update the Names of the scopes
	Public Sub Set_ScopeLabel(Channel As Integer)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If DEVICE.Connected Then
				DEVICE.Name = TextBox_SCOPE_Title.Text
				'turn on the label display
				DEVICE.Say(":display:label 1")
				'change the label
				DEVICE.Say(":channel" & oddoreven(Channel) & ":LABel """ & DEVICE.Name & """")
			End If          'Get the names
		Catch ex As Exception
		End Try
	End Sub



	'Measure FREQ
	Public Sub Get_ScopeFreq(Channel As Integer)
		Try
			CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
			If DEVICE.Connected Then
				DEVICE.Say(":MEAS:FREQ? CHAN" & oddoreven(Channel))
				DEVICE.Read.Freq = DEVICE.Listen
				If DEVICE.Read.Freq > 9.0E+20 Then
					ScopeAutoscale(Channel)
				End If
				display_freq.Value_To_Display = DEVICE.Read.Freq
			End If
		Catch ex As Exception
		End Try
	End Sub

	'measure dbm
	Public Sub DisplayDBM(Channel As Integer)
		Try
			DEVICE.Read.dBm = Convert_Vrms_to_dBM(DEVICE.Read.Vrms, UserInterfaceShell.Reff_Imp.Text)
			If DEVICE.Read.dBm > 9.9E+30 Then
				DEVICE.Read.dBm = 0
			ElseIf DEVICE.Read.dBm < -9.9E+30 Then
				DEVICE.Read.dBm = 0
			Else

			End If

			display_dBm.Value_To_Display = DEVICE.Read.dBm

		Catch ex As Exception
		End Try
	End Sub



	Public Sub Set_ScopeTriger(channel As Integer)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If DEVICE.Connected Then
				DEVICE.Say(":TRIGger:SOURce CHAN" & oddoreven(channel))
			End If
		Catch ex As Exception
		End Try
	End Sub




	'///////////////////////////////////////////////
	'HORIZONTAL SCALE
	Public Sub Get_ScopeTimescale(Channel)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try

			If DEVICE.Connected Then
				If DEVICE.Read.TimeBase = False Then
					DEVICE.Say(":TIMebase:MAIN:SCALe?")
					DEVICE.Display.X.Scale = DEVICE.Listen
					TextBox_TimeBase.Text = DEVICE.Display.X.Scale
					DEVICE.Read.TimeBase = True
				End If
			End If
		Catch ex As Exception
		End Try
	End Sub

	'HORIZONTAL SCALE
	Public Sub Set_ScopeTimescale(Channel, TimeScaleToSet)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)

		Try
			If DEVICE.Connected Then
				DEVICE.Say(":TIMebase:MAIN:SCALe " & TimeScaleToSet)
				TextBox_TimeBase.Text = TimeScaleToSet
			End If
		Catch ex As Exception
		End Try
	End Sub

	'///////////////////////////////////////////////
	'VERTICAL SCALE
	'Calculate Vertical Min and Max
	Public Sub Calculate_ScopeVerticalMinMax(channel)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		If DEVICE.Read.Vertical = False Or DEVICE.Read.Vertical = -1 Then
			GET_VerticalScale(channel)
			DEVICE.Display.Y.Minimum = -1 * (GET_ScopeVerticalRange(channel) / 2 - ScopeVerticalOffSet(channel))
			DEVICE.Display.Y.Maximum = DEVICE.Display.Y.Range / 2 + DEVICE.Display.Y.Offset
			DEVICE.Read.Vertical = True
		End If
	End Sub

	Public VoltsPerDivisionIncriments() As Double = {
		0.002, 0.005,'1ms - 5ms
		 0.01, 0.02, 0.05,'10ms - 50ms
		 0.1, 0.2, 0.5,'100ms - 500ms
		 1, 2, 5} ' 10-50s

	'SET Vertical Scale
	Public Function SET_ScopeVerticalScale(Channel, index) As Double
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If DEVICE.Connected Then
				'do some math 
				Dim VoltaScale As Double = VoltsPerDivisionIncriments(VoltsPerDivisionIncriments.Length - index)

				DEVICE.Say(":CHANnel" & oddoreven(Channel) & ":Scale " & VoltaScale)
				TextBox_vertical.Text = ConvertToEngNotation(VoltaScale) & "Volts"
				DEVICE.Display.Y.Scale = VoltaScale
			End If
		Catch ex As Exception
		End Try
	End Function

	'Get Vertical Scale
	Public Function GET_VerticalScale(Channel) As Double
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try

			If DEVICE.Connected Then
				DEVICE.Say(":CHANnel" & oddoreven(Channel) & ":Scale?")
				'pass on the truths
				DEVICE.Display.Y.Scale = DEVICE.Listen
				TextBox_vertical.Text = DEVICE.Display.Y.Scale
			End If

		Catch ex As Exception
		End Try
		Return DEVICE.Display.Y.Scale
	End Function

	'Get Vertical Range
	Public Function GET_ScopeVerticalRange(Channel) As Double
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try

			If DEVICE.Connected Then
				DEVICE.Say(":CHANnel" & oddoreven(Channel) & ":Range?")
				DEVICE.Display.Y.Range = DEVICE.Listen
			End If
		Catch ex As Exception

		End Try
		Return DEVICE.Display.Y.Range
	End Function

	'Get Vertical Offset
	Public Function ScopeVerticalOffSet(Channel) As Double
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If DEVICE.Connected Then
				DEVICE.Say(":CHANnel" & oddoreven(Channel) & ":OffSet?")
				DEVICE.Display.Y.Offset = DEVICE.Listen
			End If
		Catch ex As Exception
		End Try
		Return DEVICE.Display.Y.Offset
	End Function

	'///////////////////////////////////////////////
	'PHASE
	'Public Sub ScopeMeasurePhaseDifference(channelA As Integer, ChannelB As Integer)
	'	CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)

	'	Try
	'		Ocilliscope(channelA).Say(":MEAS:PHAS? CHAN" & channelA & ", CHAN" & ChannelB & """")
	'		'    AgilentDifference.DiffPhase = CDbl(Ocilliscope(ChannelB).Listen)
	'	Catch ex As Exception
	'		OcilliDEVICE.Connected = False
	'	End Try
	'End Sub


	'///////////////////////////////////////////////
	'GET DATA FROM SCOPE
	Public Sub Get_ScopeWaveData(Channel)
		Try
			If DEVICE.Connected Then
				CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
				DEVICE.Say(":WAV:DATA?")
				DEVICE.Read.RawWaveData = DEVICE.Listen
			End If

		Catch ex As Exception
			DEVICE.DeviceReset()
		End Try

	End Sub

	'Configure RAW DATA FROM SCOPE
	Public Sub SET_ScopeWaveConfig(channel)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)

		Try
			If DEVICE.Connected Then
				DEVICE.Say(":WAVeform:SOURce CHANnel" & oddoreven(channel))
				If DEVICE.Read.WaveForm = False Then
					'Configure source and format
					DEVICE.Say(":WAV:POINTS MAX")
					'what other formats?  are the others quicker?
					DEVICE.Say(":WAVeform:FORmat ASCii")
					DEVICE.Read.WaveForm = True
				End If
			Else
			End If
		Catch ex As Exception
		End Try
	End Sub

	Public Sub plot(channel)
		Try
			If DEVICE.Connected Then
				Set_ScopeTriger(channel)
				SET_ScopeWaveConfig(channel)
				Get_ScopeWaveData(channel)
				CHART_MATH_SplitUpRawData(channel)
				Calculate_ScopeVerticalMinMax(channel)
				Get_ScopeTimescale(channel)
				AddSplitDataToChart(channel)
				Scope_SeriesBuilding_Chart(channel)
				DisplayGraph(channel)
			End If
		Catch ex As Exception
		End Try
	End Sub


	'Split up the raw data fromt the scope
	Public Sub CHART_MATH_SplitUpRawData(Channel)
		Dim NumberOfCharactersToIgnor As Integer = 11
		DEVICE.Read.SplitWaveData = Mid(DEVICE.Read.RawWaveData, NumberOfCharactersToIgnor).Split(",")
	End Sub

	Private Sub Button_Scope_Get_Data_Click(sender As Object, e As EventArgs)
		Get_ScopeMeasureAll(channel)
	End Sub

	Private Sub TextBox_SCOPE_Title_TextChanged(sender As Object, e As EventArgs) Handles TextBox_SCOPE_Title.TextChanged
		Try
			If DEVICE.Connected Then
				Set_ScopeLabel(channel)
			End If
		Catch ex As Exception

		End Try
	End Sub

	Public Sub AddSplitDataToChart(channel)
		Dim tempDataTable As New DataTable("SCOPE CH" & channel)
		tempDataTable.Columns.Clear()
		tempDataTable.Columns.Add("SCOPE " & channel)

		For I = 0 To ((DEVICE.Read.SplitWaveData.Length) - 1)
			tempDataTable.Rows.Add(DEVICE.Read.SplitWaveData(I))
		Next I
		DEVICE.Read.DataTable = tempDataTable
	End Sub

	Public Sub Scope_SeriesBuilding_Chart(channel)
		Try
			TimeChart.Series.Dispose()
			TimeChart.Series.Clear()
			'Chart.Series.Add(DataThatWillBeGraphed)

			DEVICE.Display.X.NumberOfDivisions = 10
			DEVICE.Read.ScopeGraphSeries = New Series
			DEVICE.Read.ScopeGraphSeries.Name = "Scope " & channel
			DEVICE.Read.ScopeGraphSeries.ChartType = SeriesChartType.Spline

			DEVICE.Read.ScopeGraphSeries.Color = ChangeNumbertoColor(channel)
			TimeChart.BackColor = ChangeNumbertoColor(channel)

			'this displays the value of the datapoint
			'OcilliDEVICE.ScopeGraphSeries.Label = "Label Text"

			Scope_Time_division(channel)

			Dim TotalDataPoints As Double = DEVICE.Read.SplitWaveData.Length
			CommandList("TotalDataPoints:" & TotalDataPoints)

			Dim SecondsPerDivision As Double = DEVICE.Display.ChartScale * DEVICE.Display.X.Scale
			CommandList("SecondsPerDivision:" & SecondsPerDivision)

			Dim ScaleOfDatatPoint As Double = (SecondsPerDivision * DEVICE.Display.X.NumberOfDivisions) / TotalDataPoints
			CommandList("ScaleOfDatatPoint:" & ScaleOfDatatPoint)

			Dim PointsPerDivision As Integer = TotalDataPoints / DEVICE.Display.X.NumberOfDivisions

			'clear maximum
			DEVICE.Display.Y.Maximum = -1000
			DEVICE.Display.Y.Minimum = 1000

			'Scale the Seconds points per division over the period of the scale

			For I = 0 To ((TotalDataPoints) - 1)
				DEVICE.Read.ScopeGraphSeries.Points.AddXY(((I + 1) * ScaleOfDatatPoint * DEVICE.Display.ChartScale), DEVICE.Read.SplitWaveData(I))

				If DEVICE.Read.SplitWaveData(I) >= DEVICE.Display.Y.Maximum Then
					DEVICE.Display.Y.Maximum = DEVICE.Read.SplitWaveData(I)
				End If

				If DEVICE.Read.SplitWaveData(I) <= DEVICE.Display.Y.Minimum Then
					DEVICE.Display.Y.Minimum = DEVICE.Read.SplitWaveData(I)
				End If
			Next

			'set the x axis divisions
			DEVICE.Display.X.Division = (ScaleOfDatatPoint * PointsPerDivision * DEVICE.Display.ChartScale)
			'Data_Grid.DataSource = DEVICE.Read.DataTable
		Catch ex As Exception
		End Try

	End Sub

	Public Sub DisplayGraph(channel)

		Dim YminScaled As Double
		Dim YmaxScaled As Double

		Try
			'Add To Chart
			TimeChart.Series.Add(DEVICE.Read.ScopeGraphSeries)

			'Calculate the divisions of the horizontal lines
			YminScaled = Math.Floor((DEVICE.Display.Y.Minimum) / (DEVICE.Display.Y.Scale))
			YmaxScaled = Math.Ceiling(DEVICE.Display.Y.Maximum / (DEVICE.Display.Y.Scale))

			'Find the closest Max division based on the scale
			If YmaxScaled * DEVICE.Display.Y.Scale < DEVICE.Display.Y.Maximum Then
				YmaxScaled = YmaxScaled + 1
			End If

			'Find the closest Min division based on the scale
			If YminScaled * DEVICE.Display.Y.Scale > DEVICE.Display.Y.Minimum Then
				YminScaled = YminScaled - 1
			End If

			'Store the Y divisions and Min and Max
			DEVICE.Display.Y.Minimum = (YminScaled) * DEVICE.Display.Y.Scale
			DEVICE.Display.Y.Maximum = (YmaxScaled) * DEVICE.Display.Y.Scale
			DEVICE.Display.Y.Division = DEVICE.Display.Y.Scale

			'Store the X divisions and Min and Max
			DEVICE.Display.X.Minimum = 0
			DEVICE.Display.X.Maximum = DEVICE.Display.X.Division * DEVICE.Display.X.NumberOfDivisions
			DEVICE.Display.X.Division = DEVICE.Display.X.Division

			'Configure Chart Y min max and interval
			TimeChart.ChartAreas(0).AxisY.Minimum = DEVICE.Display.Y.Minimum
			TimeChart.ChartAreas(0).AxisY.Maximum = DEVICE.Display.Y.Maximum
			TimeChart.ChartAreas(0).AxisY.Interval = DEVICE.Display.Y.Division

			'Configure Chart X min max and interval
			TimeChart.ChartAreas(0).AxisX.Minimum = DEVICE.Display.X.Minimum
			TimeChart.ChartAreas(0).AxisX.Maximum = DEVICE.Display.X.Maximum
			TimeChart.ChartAreas(0).AxisX.Interval = DEVICE.Display.X.Division

		Catch ex As Exception

		End Try

	End Sub

	Public Sub Scope_Time_division(Channel As Integer)
		If DEVICE.Display.X.Scale < 0.001 Then
			DEVICE.Display.ChartScale = 1  'mili
			CommandList("SCALE mili")
		ElseIf DEVICE.Display.X.Scale < 0.000001 Then ' micro
			DEVICE.Display.ChartScale = 100000
			CommandList("SCALE micro")
		Else
			DEVICE.Display.ChartScale = 1
			CommandList("SCALE second")
		End If
	End Sub


	Private Sub TimeChart_Click(sender As Object, e As EventArgs) Handles TimeChart.Click
		If DEVICE.Connected Then
			plot(channel)
		Else
			DEVICE.ConnectToGPIB()
		End If
	End Sub

	Private Sub display_VPP_Load(sender As Object, e As EventArgs) Handles display_VPP.Click
		ScopeMeasureVPP(channel)
	End Sub

	Private Sub display_freq_Load(sender As Object, e As EventArgs) Handles display_freq.Click
		Get_ScopeFreq(channel)
	End Sub

	'Measure VRMS
	Public Sub ScopeMeasureVrms(Channel As Integer)
		Try
			If DEVICE.Connected Then
				CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
				DEVICE.Say(":MEAS:VRMS? CHAN" & oddoreven(Channel))
				DEVICE.Read.Vrms = DEVICE.Listen

				'Error Check it
				' check if it's HUGE or infinity
				If DEVICE.Read.Vrms > 9.9E+20 Then
					DEVICE.Read.Vrms = 0
					ScopeAutoscale(Channel)
				End If
				display_Vrms.Value_To_Display = DEVICE.Read.Vrms
			End If
		Catch ex As Exception
			ErrorList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		End Try
	End Sub


	Private Sub display_dBm_Load_1(sender As Object, e As EventArgs) Handles display_dBm.Click
		DisplayDBM(channel)
	End Sub


	Private Sub display_Vrms_Load_1(sender As Object, e As EventArgs) Handles display_Vrms.Click
		ScopeMeasureVrms(channel)
	End Sub

	Private Sub display_dBm_Load(sender As Object, e As EventArgs) Handles display_dBm.Click
		ScopeMeasureVrms(channel)
		DisplayDBM(channel)
	End Sub

	Private Sub display_Vrms_Load(sender As Object, e As EventArgs) Handles display_Vrms.Click
		ScopeMeasureVrms(channel)
		DisplayDBM(channel)
	End Sub

	Public Sub ConfigureFFT(Channel As Integer, Center As Double, Span As Double)

		If DEVICE.Connected Then
			DEVICE.Say(":CHANnel1:DISPlay 0") ' Shut off the channel 1 
			DEVICE.Say(":CHANnel2:DISPlay 0") ' Shut off the channel 1 
			DEVICE.Say(":TIMebase:MAIN:SCALe 0.00340")


			DEVICE.Say(":FUNCtion:OPERation FFT") 'loadfft
			DEVICE.Say(":FUNCtion:Display 1") 'display it
			DEVICE.Say(":FUNCtion:SOURce Chan" & CInt(oddoreven(Channel)))  'display it
			DEVICE.Say(":RUN") 'display it

			DEVICE.Say(":FUNCtion:SPAN " & Span) 'display it
			DEVICE.Say(":FUNCtion:CENTer " & Center) 'display it

			DEVICE.Say(":FUNCtion:SCALe 20") 'display it
			DEVICE.Say(":FUNCtion:OFFSet 0") 'display it


		End If

	End Sub


	Public LOOKUP_SecondsPerDivisionIncriments() As Double = {
		0.000000005,'5ns
		0.00000001, 0.00000002, 0.00000005,'10ns - 50ns
		0.0000001, 0.0000002, 0.0000005,'100ns -500ns
		0.000001, 0.000002, 0.000005,'1us - 5us
		0.00001, 0.00002, 0.00005,'10us - 50us
		0.0001, 0.0002, 0.0005,'100us - 500us
		 0.001, 0.002, 0.005,'1ms - 5ms
		 0.01, 0.02, 0.05,'10ms - 50ms
		 0.1, 0.2, 0.5,'100ms - 500ms
		 1, 2, 5,'1 - 5 seconds
		 10, 20, 50} ' 10-50s


	Private Sub Button_RouteMe_Click(sender As Object, e As EventArgs) Handles Button_RouteMe.TextChanged
		sender.BackColor = APK_Bench_Router.AllowBus(sender, RouterConnection)
	End Sub

	Private Sub Button_RouteMe_Click_1(sender As Object, e As EventArgs) Handles Button_RouteMe.Click



		sender.BackColor = APK_Bench_Router.AllowBus(sender, RouterConnection)





		UserInterfaceShell.TableLayoutPanel_MatrixCoax_000.Location = New Point(UserInterfaceShell.TableLayoutPanel_Scopes.Location.X + Me.Location.X, Me.Location.Y + 20)
	End Sub

	Private Sub FFT_Click(sender As Object, e As EventArgs) Handles Button_FFT.Click
		ConfigureFFT(channel, 15000, 30000)

		If Button_FFT.BackColor = Color.Orange Then
			Button_FFT.BackColor = Color.Transparent
		Else
			Button_FFT.BackColor = Color.Orange
		End If
	End Sub

	Private Sub display_freq_Load_1(sender As Object, e As EventArgs) Handles display_freq.Click
		Get_ScopeFreq(channel)
	End Sub



	'///////////////////////////////////////////////
	'MEASUREMENTS

	'Measure VPP
	Public Sub ScopeMeasureVPP(Channel As Integer)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		Try
			If DEVICE.Connected Then
				DEVICE.Say(":MEAS:VPP? CHAN" & oddoreven(Channel))
				DEVICE.Read.Vpp = DEVICE.Listen
				If DEVICE.Read.Vpp > 9.0E+20 Then
					ScopeAutoscale(Channel)
				End If
				display_VPP.Value_To_Display = DEVICE.Read.Vpp
			End If
		Catch ex As Exception
		End Try
	End Sub

	Private Sub display_VPP_Load_1(sender As Object, e As EventArgs) Handles display_VPP.Click
		ScopeMeasureVPP(channel)
	End Sub



	Private Sub TrackBar2_Scroll_1(sender As Object, e As EventArgs) Handles TrackBar_Vertical.Scroll
		SET_ScopeVerticalScale(channel, TrackBar_Vertical.Value)
	End Sub

	'///////////////////////////////////////////////
	'AUTOSCALE

	Private Sub Button_Autoscale_Click(sender As Object, e As EventArgs) Handles Button_Autoscale.Click
		ScopeAutoscale(channel)
	End Sub

	Public Sub ScopeAutoscale(channel)
		Try
			If DEVICE.Connected Then
				CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
				DEVICE.Say("AUToscale")
				DEVICE.Read.TimeBase = False
				DEVICE.Read.Vertical = False
				DEVICE.Read.WaveForm = False
			Else
				DEVICE.DeviceReset()
			End If
		Catch ex As Exception
			ErrorList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		End Try
	End Sub

	Private Sub CheckBox_freq_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_freq.CheckedChanged
		display_freq.Visible = CheckBox_freq.Checked
	End Sub

	Private Sub CheckBox_VPP_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_VPP.CheckedChanged
		display_VPP.Visible = CheckBox_VPP.Checked
	End Sub

	Private Sub CheckBox_Vrms_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Vrms.CheckedChanged
		display_Vrms.Visible = CheckBox_Vrms.Checked
		display_dBm.Visible = CheckBox_Vrms.Checked
	End Sub

	Private Sub TrackBar_GraphDelay_Scroll(sender As Object, e As EventArgs)
		GraphDelayCount = 0
	End Sub


	Private Sub TrackBar_Horizontal_Scroll(sender As Object, e As EventArgs) Handles TrackBar_Horizontal.Scroll
		Set_ScopeTimescale(channel, LOOKUP_SecondsPerDivisionIncriments(LOOKUP_SecondsPerDivisionIncriments.Length - TrackBar_Horizontal.Value - 1))
		TextBox_TimeBase.Text = ConvertToEngNotation(LOOKUP_SecondsPerDivisionIncriments(LOOKUP_SecondsPerDivisionIncriments.Length - TrackBar_Horizontal.Value - 1)) & "Seconds"
	End Sub

	Private Sub CheckBox_AveragingChanged(sender As Object, e As EventArgs) Handles CheckBox_Averaging.CheckedChanged
		Scope_Averaging(channel, TrackBar_Number_Of_Averages.Value, CheckBox_Averaging.Checked)
	End Sub

	'AVERAGEING FUNCTION
	Private Sub Scope_Averaging(Channel As Integer, Number_Of_Averages As Integer, On_or_Off As Boolean)
		CommandList(System.Reflection.MethodBase.GetCurrentMethod.Name)
		If DEVICE.Connected Then
			If On_or_Off Then
				DEVICE.Say(":ACQuire:TYPE AVER")
				DEVICE.Say(":ACQuire:COUNT " & Number_Of_Averages)
			Else
				DEVICE.Say(":ACQuire:TYPE NORM")
			End If
		End If
	End Sub

End Class
