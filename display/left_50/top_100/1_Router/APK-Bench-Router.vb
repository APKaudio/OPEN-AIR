Public Class APK_Bench_Router

	Public DEVICE As BenchInstrumentItem
	Dim AllowedBus As Integer
	Dim AllowedCrossPoint As Integer

	Dim relay(1000) As Boolean


	Private Sub Balanced_Router_reposition(sender As Object, e As EventArgs) Handles MyBase.Move
		Me.Text = "SOFTWARE " & " LOCATION X:" & Me.Location.X & " LOCATION Y:" & Me.Location.Y & " WIDTH:" & Me.Width & " HEIGHT:" & Me.Height
	End Sub

	Private Sub APK_Bench_Router_Load(sender As Object, e As EventArgs) Handles MyBase.Load
		SetupRouter()
	End Sub

	Public Sub SetupRouter()
		DEVICE = New BenchInstrumentItem
		DEVICE.Name = "Bench Mux"
		DEVICE.Address.GPIB_Address = 10
		DEVICE.Address.IP = "44.44.44.222"
		DEVICE.Address.GPIB_Bus = "gpib7"

		DEVICE.ConnectToGPIB()
	End Sub




	Public Function AllowBus(sender As Object, NewlyAllowedBus As Integer)

		If relay(NewlyAllowedBus) = False Then
			AllowedBus = NewlyAllowedBus

			relay(NewlyAllowedBus) = True
			Return ChangeNumbertoColor(AllowedBus)

		ElseIf relay(NewlyAllowedBus) Then
			relay(NewlyAllowedBus) = False
			Return Color.Transparent
		End If




	End Function

	Public Function AllowCrossOver(NewlyAllowedBus As Integer)

		If AllowedBus = -1 Then
		Else
			If AllowedBus <> NewlyAllowedBus Then
				AllowedBus = NewlyAllowedBus
				Return ChangeNumbertoColor(AllowedBus)
			Else
				AllowedBus = 0
				Return Color.Transparent
			End If
		End If

	End Function


	Public Function ConnectWithAllowedBus(sender As Object, portNumber As Integer)
		If AllowedBus = -1 Then
			Return Color.Transparent
		Else
			If AllowedBus > 100 Then


				portNumber = portNumber + 100
			End If

			''
			If sender.backcolor = Color.Transparent Then
				DEVICE.Say("Connect " & portNumber & "," & AllowedBus)

				Return ChangeNumbertoColor(AllowedBus)
				AllowedBus = -1

			Else
				DEVICE.Say("Disconn " & portNumber & "," & AllowedBus)

				Return Color.Transparent
				AllowedBus = -1

			End If
		End If

	End Function


	Public Function ConnectCrossPointLatch(sender As Object, portNumber As Integer)
		If sender.backcolor = Color.Transparent Then
			DEVICE.Say("CLOSE " & portNumber)

			Return ChangeNumbertoColor(portNumber)

		Else
			DEVICE.Say("OPEN " & portNumber)

			Return Color.Transparent
		End If
	End Function



	Public Sub Route(Route_From As Integer, Route_To As Integer)
		DEVICE.Say("connect " & Route_From & ", " & Route_To)
	End Sub




	Dim Module_name_IO As Integer = 900


	''Balanced Sound Sources
	Private Sub Button_XFMR_OUT_L_Click(sender As Object, e As EventArgs) Handles Button_XFMR_OUT_L_701.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 1)
	End Sub

	Private Sub Button_XFMR_OUT_R_Click(sender As Object, e As EventArgs) Handles Button_OUT_R_721.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 21)
	End Sub

	Private Sub Button_NEUTRIK_OUT_L_Click(sender As Object, e As EventArgs) Handles Button_NEUTRIK_OUT_L_703.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 3)
	End Sub

	Private Sub Button_NEUTRIK_OUT_R_Click(sender As Object, e As EventArgs) Handles Button_OUT_R_723.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 23)
	End Sub

	Private Sub Button_Music_L_Click(sender As Object, e As EventArgs) Handles Button_Music_L_704.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 4)

	End Sub

	Private Sub Button_Music_R_Click(sender As Object, e As EventArgs) Handles Button_OUT_R_724.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 24)


	End Sub




	''BALANCE ANALYZERS
	Private Sub Button_XFMR_IN_L_Click(sender As Object, e As EventArgs) Handles Button_IN_L_711.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 11)
	End Sub

	Private Sub Button_XFMR_IN_R_Click(sender As Object, e As EventArgs) Handles Button_IN_R_731.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 31)
	End Sub

	Private Sub Button_NEUTRIK_IN_L_Click(sender As Object, e As EventArgs) Handles Button_IN_L_712.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 12)
	End Sub

	Private Sub Button_NEUTRIK_IN_R_Click(sender As Object, e As EventArgs) Handles Button_IN_R_732.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 32)
	End Sub

	Private Sub Button_SLM_L_Click(sender As Object, e As EventArgs) Handles Button_IN_L_713.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 13)
	End Sub

	Private Sub Button_SLM_R_Click(sender As Object, e As EventArgs) Handles Button_IN_R_733.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 33)
	End Sub

	Private Sub Button_Monitor_1_L_Click(sender As Object, e As EventArgs)
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 14)
	End Sub

	Private Sub Button_Monitor_1_R_Click(sender As Object, e As EventArgs)
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 34)
	End Sub

	Private Sub Button_Monitor_2_L_Click(sender As Object, e As EventArgs) Handles Button_IN_L_714.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 14)
	End Sub

	Private Sub Button_Monitor_2_R_Click(sender As Object, e As EventArgs) Handles Button_IN_R_734.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 34)
	End Sub

	Private Sub Button_AUX_OUT_L_702_Click(sender As Object, e As EventArgs) Handles Button_AUX_OUT_L_702.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 2)

	End Sub

	Private Sub Button_AUX_OUT_R_712_Click(sender As Object, e As EventArgs) Handles Button_OUT_R_722.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 22)

	End Sub




	''BalaNCED SOURCE BUS CONNECTION
	Private Sub Button_BAL_AB0_790_Click(sender As Object, e As EventArgs) Handles Button_BAL_AB0_790.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 90)
	End Sub

	Private Sub Button_BAL_AB2_Click(sender As Object, e As EventArgs) Handles Button_BAL_AB2_792.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 92)
	End Sub

	Private Sub Button_BAL_AB1_791_Click(sender As Object, e As EventArgs) Handles Button_BAL_AB1_791.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 91)
	End Sub

	Private Sub Button_BAL_AB3_793_Click(sender As Object, e As EventArgs) Handles Button_BAL_AB3_793.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 93)
	End Sub

	'BYPASSES

	Private Sub Button_Bypass_70_Click(sender As Object, e As EventArgs) Handles Button_Bypass_70.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 70)
	End Sub

	Private Sub Button_Bypass_72_Click(sender As Object, e As EventArgs) Handles Button_Bypass_72.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_IO + 72)
	End Sub


	Dim Module_name_EDAC_1_12 As Integer = 600
	Dim Module_name_EDAC_13_24 As Integer = 700
	Dim Module_name_EDAC_25_36 As Integer = 800

	'' EDAC OUTPUTS 1-36
	Private Sub Button_EDAC_OUT_A_1_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_1_401.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 1)
	End Sub

	Private Sub Button_EDAC_OUT_A_2_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_2_421.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 21)
	End Sub

	Private Sub Button_EDAC_OUT_A_3_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_3_402.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 2)
	End Sub

	Private Sub Button_EDAC_OUT_A_4_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_4_422.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 22)
	End Sub

	Private Sub Button_EDAC_OUT_A_5_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_5_403.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 3)
	End Sub

	Private Sub Button_EDAC_OUT_A_6_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_6_423.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 23)
	End Sub

	Private Sub Button_EDAC_OUT_A_7_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_7_404.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 4)
	End Sub

	Private Sub Button_EDAC_OUT_A_8_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_8_424.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 24)
	End Sub

	Private Sub Button_EDAC_OUT_A_9_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_9_405.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 5)
	End Sub

	Private Sub Button_EDAC_OUT_A_10_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_10_425.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 25)
	End Sub

	Private Sub Button_EDAC_OUT_A_11_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_11_406.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 6)
	End Sub

	Private Sub Button_EDAC_OUT_A_12_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_12_426.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 26)
	End Sub

	Private Sub Button_EDAC_OUT_B_13_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_13_501.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 1)
	End Sub

	Private Sub Button_EDAC_OUT_B_14_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_14_521.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 21)
	End Sub

	Private Sub Button_EDAC_OUT_B_15_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_15_502.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 2)
	End Sub

	Private Sub Button_EDAC_OUT_B_16_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_16_522.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 22)
	End Sub

	Private Sub Button_EDAC_OUT_B_17_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_17_503.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 3)
	End Sub

	Private Sub Button_EDAC_OUT_B_18_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_18_523.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 23)
	End Sub

	Private Sub Button_EDAC_OUT_B_19_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_19_504.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 4)
	End Sub

	Private Sub Button_EDAC_OUT_B_20_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_20_524.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 24)
	End Sub

	Private Sub Button_EDAC_OUT_B_21_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_21_505.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 5)
	End Sub

	Private Sub Button_EDAC_OUT_B_22_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_22_525.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 25)
	End Sub

	Private Sub Button_EDAC_OUT_B_23_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_23_506.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 6)
	End Sub

	Private Sub Button_EDAC_OUT_B_24_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_24_526.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 26)
	End Sub

	Private Sub Button_EDAC_OUT_C_25_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_25_601.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 1)
	End Sub

	Private Sub Button_EDAC_OUT_C_26_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_26_621.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 21)
	End Sub

	Private Sub Button_EDAC_OUT_C_27_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_27_602.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 2)
	End Sub

	Private Sub Button_EDAC_OUT_C_28_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_28_622.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 22)
	End Sub

	Private Sub Button_EDAC_OUT_C_29_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_29_603.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 3)
	End Sub

	Private Sub Button_EDAC_OUT_C_30_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_30_623.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 23)
	End Sub

	Private Sub Button_EDAC_OUT_C_31_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_31_604.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 4)
	End Sub

	Private Sub Button_EDAC_OUT_C_32_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_32_624.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 24)
	End Sub

	Private Sub Button_EDAC_OUT_C_33_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_33_605.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 5)
	End Sub

	Private Sub Button_EDAC_OUT_C_34_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_34_625.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 25)
	End Sub

	Private Sub Button_EDAC_OUT_C_35_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_35_606.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 6)
	End Sub

	Private Sub Button_EDAC_OUT_C_36_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_36_626.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 26)
	End Sub



	'' EDAC INPUTS
	Private Sub Button_EDAC_IN_A_1_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_1_411.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 11)
	End Sub

	Private Sub Button_EDAC_IN_A_2_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_2_431.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 31)
	End Sub

	Private Sub Button_EDAC_IN_A_3_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_3_412.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 12)
	End Sub

	Private Sub Button_EDAC_IN_A_4_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_4_432.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 32)
	End Sub

	Private Sub Button_EDAC_IN_A_5_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_5_413.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 13)
	End Sub

	Private Sub Button_EDAC_IN_A_6_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_6_433.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 33)
	End Sub

	Private Sub Button_EDAC_IN_A_7_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_7_414.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 14)
	End Sub

	Private Sub Button_EDAC_IN_A_8_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_8_434.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 34)
	End Sub

	Private Sub Button_EDAC_IN_A_9_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_9_415.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 15)
	End Sub

	Private Sub Button_EDAC_IN_A_10_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_10_435.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 35)
	End Sub

	Private Sub Button_EDAC_IN_A_11_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_11_416.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 16)
	End Sub

	Private Sub Button_EDAC_IN_A_12_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_12_436.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 36)
	End Sub

	Private Sub Button_EDAC_IN_B_13_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_13_511.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 11)
	End Sub

	Private Sub Button_EDAC_IN_B_14_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_14_531.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 31)
	End Sub

	Private Sub Button_EDAC_IN_B_15_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_15_512.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 12)
	End Sub

	Private Sub Button_EDAC_IN_B_16_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_16_532.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 32)
	End Sub

	Private Sub Button_EDAC_IN_B_17_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_17_513.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 13)
	End Sub

	Private Sub Button_EDAC_IN_B_18_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_18_533.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 33)
	End Sub

	Private Sub Button_EDAC_IN_B_19_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_19_514.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 14)
	End Sub

	Private Sub Button_EDAC_IN_B_20_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_20_534.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 34)
	End Sub

	Private Sub Button_EDAC_IN_B_21_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_21_515.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 15)
	End Sub

	Private Sub Button_EDAC_IN_B_22_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_22_535.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 35)
	End Sub

	Private Sub Button_EDAC_IN_B_23_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_23_516.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 16)
	End Sub

	Private Sub Button_EDAC_IN_B_24_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_24_536.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 36)
	End Sub

	Private Sub Button_EDAC_IN_C_25_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_25_611.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 11)
	End Sub

	Private Sub Button_EDAC_IN_C_26_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_26_631.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 31)
	End Sub

	Private Sub Button_EDAC_IN_C_27_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_27_612.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 12)
	End Sub

	Private Sub Button_EDAC_IN_C_28_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_28_632.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 32)
	End Sub

	Private Sub Button_EDAC_IN_C_29_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_29_613.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 13)
	End Sub

	Private Sub Button_EDAC_IN_C_30_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_30_633.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 33)
	End Sub

	Private Sub Button_EDAC_IN_C_31_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_31_614.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 14)
	End Sub

	Private Sub Button_EDAC_IN_C_32_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_32_634.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 34)
	End Sub

	Private Sub Button_EDAC_IN_C_33_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_33_615.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 15)
	End Sub

	Private Sub Button_EDAC_IN_C_34_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_34_635.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 35)
	End Sub

	Private Sub Button_EDAC_IN_C_35_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_35_616.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 16)
	End Sub

	Private Sub Button_EDAC_IN_C_36_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_36_636.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 36)
	End Sub






	''''EDAC OUTPUT XLR MALE - BUS CONNECTION 
	Private Sub Button_EDAC_OUT_A_L_490_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_L_490.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 90)
	End Sub

	Private Sub Button_EDAC_OUT_A_R_492_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_A_R_492.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 92)
	End Sub

	Private Sub Button_EDAC_OUT_B_L_590_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_L_590.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 90)
	End Sub

	Private Sub Button_EDAC_OUT_B_R_592_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_B_R_592.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 2)
	End Sub

	Private Sub Button_EDAC_OUT_C_L_690_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_L_690.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 90)
	End Sub

	Private Sub Button_EDAC_OUT_C_R_592_Click(sender As Object, e As EventArgs) Handles Button_EDAC_OUT_C_R_692.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 92)
	End Sub



	''EDAC INPUT XLR FEMALE - BUS CONNECTION 
	Private Sub Button_EDAC_IN_A_Click(sender As Object, e As EventArgs)
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 91)
	End Sub

	Private Sub Button_EDAC_IN_A_R_493_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_A_R_493.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_1_12 + 93)
	End Sub

	Private Sub Button_EDAC_IN_B_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_L_591.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 91)
	End Sub

	Private Sub Button_EDAC_IN_B_R_593_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_B_R_593.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_13_24 + 93)
	End Sub

	Private Sub Button_EDAC_IN_C_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_L_691.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 91)
	End Sub

	Private Sub Button_EDAC_IN_C_R_693_Click(sender As Object, e As EventArgs) Handles Button_EDAC_IN_C_R_693.Click
		sender.BackColor = ConnectCrossPointLatch(sender, Module_name_EDAC_25_36 + 93)
	End Sub




	Private Sub Button_Reset_Router_Click(sender As Object, e As EventArgs) Handles Button_Reset_Router.Click
		DEVICE.Say("open 000-999")
	End Sub


End Class