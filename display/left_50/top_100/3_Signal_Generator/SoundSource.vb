Public Class SoundSource



	Public SweepStepsCollection(100000) As Double

	Public DEVICE As New BenchInstrumentItem



	Public Sub SetupSigGenConfig()


		''This is My session description
		DEVICE.Address.GPIB_Address = 20
		DEVICE.Address.IP = "44.44.44.33"
		DEVICE.Name = "Signal Gen"
		DEVICE.Address.GPIB_Bus = "gpib7"


		''SignalGen.ConnectToGPIB()
		DEVICE.ConnectToIP()


		DEVICE.Configuration.Impedance = UserInterfaceShell.Reff_Imp.Text
		If DEVICE.Connected Then
			config_SigGen()
			'Rest The Displays
			SigGen_amp.Text = 1
			SigGen_Amp_unit.SelectedIndex = 0
			SigGen_Signal_Type.SelectedIndex = 0
		Else
			'Me.Dispose()
			Me.Visible = False


		End If



	End Sub

	Public Sub config_SigGen()

		If DEVICE.Connected Then
			SGChangeLoad(DEVICE.Configuration.Impedance)
			SGChangeFunction(DEVICE.Configuration.WaveformShape)
			SGChangeFreq(DEVICE.Configuration.Freq)
			SGChangeAmplitude(DEVICE.Configuration.Amplitude)
			SGChangeAmplitudeUnit(DEVICE.Configuration.Units)
		Else


		End If

	End Sub

	Public Sub SGChangeLoad(Load As Integer)
		DEVICE.Configuration.Impedance = Load
		Try
			If DEVICE.Connected Then
				CommandList("SG: Update Source load" & DEVICE.Configuration.Impedance)
				DEVICE.Say("OUTPUT:LOAD " & DEVICE.Configuration.Impedance)
				DEVICE.Say("OUTPUT:LOAD?")
				DEVICE.Read.Impedance = DEVICE.Listen
			End If

		Catch ex As Exception
			ErrorList("ERROR: SG: Update Source load")
		End Try
	End Sub

	Public Sub SGChangeFunction(Func As String)
		DEVICE.Configuration.WaveformShape = Func
		Try
			If DEVICE.Connected Then

				CommandList("SG: Update Function" & DEVICE.Configuration.WaveformShape)
				DEVICE.Say("FUNC " & DEVICE.Configuration.WaveformShape)

				DEVICE.Say("FUNC?")
				DEVICE.Read.WaveformShape = DEVICE.Listen
			End If

		Catch ex As Exception
			ErrorList("ERROR: SG: Update Function")
		End Try
	End Sub

	Public Sub SGChangeFreq(Freq As Integer)

		Try
			If DEVICE.Connected Then





				CommandList("SG: Update Freq" & Freq)
				DEVICE.Say("FREQ " & Freq)

				DEVICE.Say("FREQ? ")
				DEVICE.Configuration.Freq = DEVICE.Listen()
				DEVICE.Read.Freq = DEVICE.Configuration.Freq

				SigGen_FrequencyTrackBar.Value = DEVICE.Read.Freq
				SigGen_Sine_freq.Text = 	DEVICE.Read.Freq




			End If

		Catch ex As Exception
			ErrorList("ERROR: SG: Update Freq")
		End Try


	End Sub

	Public Sub SGChangeAmplitude(Amplitude As String)

		Try

			If DEVICE.Connected Then
				DEVICE.Configuration.Amplitude = Amplitude

				CommandList("SG: Update Voltage" & DEVICE.Configuration.Amplitude)
				DEVICE.Say("VOLT " & DEVICE.Configuration.Amplitude)

				DEVICE.Say("VOLT?")
				DEVICE.Read.Amplitude = DEVICE.Listen()


				If SigGen_amp.Text = DEVICE.Read.Amplitude Then
					'do nothing if the input = output
				Else
					'Update if it's new
					SigGen_amp.Text = DEVICE.Read.Amplitude
				End If
			End If

		Catch ex As Exception
			ErrorList("ERROR: SG: Update Voltage")
		End Try


	End Sub

	Public Sub SGChangeAmplitudeUnit(Unit As String)
		DEVICE.Configuration.Units = Unit


		Try
			If DEVICE.Connected Then
				CommandList("SG: Update Voltage Unit" & DEVICE.Configuration.Units)
				DEVICE.Say("VOLT:UNIT " & DEVICE.Configuration.Units)

				DEVICE.Say("VOLT:UNIT?")
				DEVICE.Read.Units = DEVICE.Listen

			End If

		Catch ex As Exception
			ErrorList("ERROR: SG: Update Freq")
		End Try


	End Sub


	Public Sub FrequencyUpdate(freq As Integer)
		DEVICE.Configuration.Freq = freq


		Try
			If DEVICE.Connected Then
				CommandList("SG: Frequency update to ")

				DEVICE.Say("FREQ " & freq)
			End If

		Catch ex As Exception
			ErrorList("ERROR: Frequency update to " & freq)
		End Try

	End Sub

	Public Sub SigGen_ON()
		Try
			If DEVICE.Connected Then
				CommandList("SG: OUTPUT ON")
				DEVICE.Say("OUTPUT ON")

				DEVICE.Say("OUTPUT?")
				DEVICE.Output = DEVICE.Listen
			End If


		Catch ex As Exception
			ErrorList("ERROR SG: OUTPUT ON")
		End Try
	End Sub

	Public Sub SigGen_OFF()
		Try
			If DEVICE.Connected Then
				CommandList("SG: OUTPUT OFF")
				DEVICE.Say("OUTPUT OFF")

				DEVICE.Say("OUTPUT?")
				DEVICE.Output = DEVICE.Listen

			End If
		Catch ex As Exception
			ErrorList("ERROR SG: OUTPUT OFF")
		End Try
	End Sub

	Public Sub SGSweepCalculate()
		Dim offset As Integer = SequenceTimer.SequenceCount.CountLoops
		DEVICE.Sweep.StartPoint = CInt(SequenceTimer.SweepStart.Text)
		DEVICE.Sweep.StoppingPoint = CInt(SequenceTimer.SweepStop.Text)
		DEVICE.Sweep.Steps = CInt(SequenceTimer.Textbox_NumberOfTestCycles.Text)
		DEVICE.Sweep.StepValue = (DEVICE.Sweep.StoppingPoint - DEVICE.Sweep.StartPoint) / DEVICE.Sweep.Steps

		If SequenceTimer.CheckBox_log.Checked And (offset <= 4) Then
			SweepStepsCollection = GenerateLogSpace(DEVICE.Sweep.StartPoint + (offset), DEVICE.Sweep.StoppingPoint + (100 * offset), DEVICE.Sweep.Steps)
		ElseIf SequenceTimer.CheckBox_log.Checked And (offset > 20) Then
			For i As Integer = 0 To DEVICE.Sweep.Steps - 1
				SweepStepsCollection(i) = DEVICE.Sweep.StartPoint + i + ((offset - 20) * 10)
			Next
		ElseIf SequenceTimer.CheckBox_log.Checked And (offset > 10) Then
			SweepStepsCollection = GenerateLogSpace(DEVICE.Sweep.StartPoint + (10 * (offset - 10)), DEVICE.Sweep.StoppingPoint + (100 * offset - 10), DEVICE.Sweep.Steps)
		ElseIf SequenceTimer.CheckBox_log.Checked And (offset > 4) Then
			SweepStepsCollection = GenerateLogSpace(DEVICE.Sweep.StartPoint + (10 * (offset)), DEVICE.Sweep.StoppingPoint, DEVICE.Sweep.Steps)
		Else
			For i As Integer = 0 To DEVICE.Sweep.Steps - 1
				SweepStepsCollection(i) = DEVICE.Sweep.StartPoint + (i * DEVICE.Sweep.StepValue)
			Next
		End If
	End Sub


	Private Shared Function GenerateLogSpace(ByVal min As Integer, ByVal max As Integer, ByVal logBins As Integer)

		Dim logarithmicBase As Double = Math.E
		Dim logMin As Double = Math.Log(min)
		Dim logMax As Double = Math.Log(max)
		Dim delta As Double = (logMax - logMin) / logBins
		Dim indexes As Integer() = New Integer(logBins + 1 - 1) {}
		Dim accDelta As Double = 0
		Dim v As Single() = New Single(logBins - 1) {}

		Dim Bins(logBins - 1) As Double


		For i As Integer = 0 To logBins - 1
			v(i) = CSng(Math.Pow(logarithmicBase, logMin + accDelta))
			accDelta += delta
			Bins(i) = v(i)
		Next
		Return Bins

	End Function

	Public Sub sgsweep()


		If DEVICE.Sweep.Enable = True Then

			DEVICE.Sweep.Index = DEVICE.Sweep.Index + 1
			If DEVICE.Sweep.Index = DEVICE.Sweep.Steps Then
				DEVICE.Sweep.Index = 0
			End If
			SGChangeFreq(SweepStepsCollection(DEVICE.Sweep.Index))
		End If

	End Sub

	Public Sub DutyCycle(DutyCycle As Integer)
		DEVICE.Configuration.DutyCycle = DutyCycle
		Try
			If DEVICE.Connected Then
				CommandList("SG: DUTY CYCLE SCROLL " & DEVICE.Configuration.DutyCycle)
				If DEVICE.Configuration.WaveformShape = "SQU" Then
					DEVICE.Say("FUNC:SQU:DCYC " & DEVICE.Configuration.DutyCycle)
				ElseIf DEVICE.Configuration.WaveformShape = "RAMP" Then
					DEVICE.Say("FUNC:RAMP:SYMM " & DEVICE.Configuration.DutyCycle)
				End If
			End If

		Catch ex As Exception

		End Try

	End Sub







	'DISPLAY--------------------------------------------


	Private Sub SoundSource_Load(sender As Object, e As EventArgs) Handles MyBase.Load

		Try
			SetupSigGenConfig()
		Catch ex As Exception
			'	Me.Dispose()
			Me.Visible = False
		End Try




	End Sub





	Private Sub ButtSignalOnOff_Click(sender As Object, e As EventArgs) Handles ButtSignalOnOff.Click
		If ButtSignalOnOff.Text = "OFF" Then
			Try
				SigGen_ON()

				If DEVICE.Output Then
					ButtSignalOnOff.Text = "ON"
					ButtSignalOnOff.BackColor = Color.DarkOrange
				Else


				End If

			Catch ex As Exception

			End Try



		Else
			SigGen_OFF()
			ButtSignalOnOff.Text = "OFF"
			ButtSignalOnOff.BackColor = Color.DarkGray
		End If
	End Sub


	Private Sub TextBox1_TextChanged(sender As Object, e As EventArgs) Handles TextBox_TimeUnits.TextChanged
		Try

			If SigGen_Sine_freq.Text = (1 / TextBox_TimeUnits.Text) Then

			Else
				SigGen_Sine_freq.Text = 1 / TextBox_TimeUnits.Text

			End If



		Catch ex As Exception

		End Try

	End Sub

	Private Sub SigGen_Signal_Type_SelectedIndexChanged(sender As Object, e As EventArgs) Handles SigGen_Signal_Type.SelectedIndexChanged
		SGChangeFunction(SigGen_Signal_Type.Text)
	End Sub


	'TAB SWEEP

	Public Sub SweepEnable_Click()

		If SequenceTimer.SweepEnable.BackColor = Color.DarkGray Then
			SequenceTimer.SweepEnable.BackColor = Color.DarkOrange
			SGSweepCalculate()
			DEVICE.Sweep.Index = 0
			DEVICE.Sweep.Enable = True
		Else
			SequenceTimer.SweepEnable.BackColor = Color.DarkGray
			DEVICE.Sweep.Enable = False
		End If

	End Sub




	Private Sub PictureBox_SignalGen_Click(sender As Object, e As EventArgs)
		If Me.Width = 325 Then
			Me.Width = 125
			Me.Height = 125
		Else

			Me.Width = 325
			Me.Height = 175
		End If


	End Sub
	Private Sub SigGen_amp_TextChanged(sender As Object, e As EventArgs) Handles SigGen_Amp_unit.SelectedIndexChanged, SigGen_amp.TextChanged

		SGChangeAmplitudeUnit(SigGen_Amp_unit.Text)
		SGChangeAmplitude(SigGen_amp.Text)
	End Sub








	Private Sub QuickFreq10Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq10Hz.CheckedChanged
		SGChangeFreq(10)

	End Sub

	Private Sub QuickFreq20Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq20Hz.CheckedChanged
		SGChangeFreq(20)
	End Sub

	Private Sub QuickFreq50Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq50Hz.CheckedChanged
		SGChangeFreq(50)
	End Sub

	Private Sub QuickFreq100Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq100Hz.CheckedChanged
		SGChangeFreq(100)
	End Sub

	Private Sub QuickFreq200Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq200Hz.CheckedChanged
		SGChangeFreq(200)
	End Sub

	Private Sub QuickFreq500Hz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq500Hz.CheckedChanged
		SGChangeFreq(500)
	End Sub

	Private Sub QuickFreq1kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq1kHz.CheckedChanged
		SGChangeFreq(1000)
	End Sub

	Private Sub QuickFreq2kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq2kHz.CheckedChanged
		SGChangeFreq(2000)
	End Sub

	Private Sub QuickFreq5kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq5kHz.CheckedChanged
		SGChangeFreq(5000)
	End Sub

	Private Sub QuickFreq10kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq10kHz.CheckedChanged
		SGChangeFreq(10000)
	End Sub

	Private Sub QuickFreq20kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq20kHz.CheckedChanged
		SGChangeFreq(20000)
	End Sub

	Private Sub QuickFreq50kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq50kHz.CheckedChanged
		SGChangeFreq(50000)
	End Sub

	Private Sub QuickFreq100kHz_CheckedChanged(sender As Object, e As EventArgs) Handles QuickFreq100kHz.CheckedChanged
		SGChangeFreq(100000)
	End Sub

	Private Sub RadioButton1_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton1.CheckedChanged
		SGChangeFreq(200000)
	End Sub

	Private Sub RadioButton2_CheckedChanged(sender As Object, e As EventArgs) Handles RadioButton2.CheckedChanged
		SGChangeFreq(500000)
	End Sub

	Private Sub SigGen_FrequencyTrackBar_Scroll_1(sender As Object, e As EventArgs) Handles SigGen_FrequencyTrackBar.Scroll
		If SigGen_FrequencyTrackBar.Value = DEVICE.Configuration.Freq Then
			'do nothing
		Else
			SGChangeFreq(SigGen_FrequencyTrackBar.Value)
			SigGen_Sine_freq.Text = DEVICE.Configuration.Freq

		End If


	End Sub





	Private Sub SigGen_Sine_freq_TextChanged(sender As Object, e As EventArgs) Handles SigGen_Sine_freq.TextChanged



		Try
			If SigGen_Sine_freq.Text = DEVICE.Configuration.Freq Then

			Else
				'Local Display
				SGChangeFreq(CDbl(SigGen_Sine_freq.Text))
				TextBox_TimeUnits.Text = 1 / SigGen_Sine_freq.Text
				SigGen_FrequencyTrackBar.Value = DEVICE.Configuration.Freq


			End If


		Catch ex As Exception
		End Try
	End Sub



End Class
