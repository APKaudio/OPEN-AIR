Public Class Router


	Public multiplexoreDACrOUTER As BenchInstrumentItem

	'routing
	Public DUT_input As SwitcherChannel
	Public DUT_Output As SwitcherChannel
	Public Test_Input As SwitcherChannel
	Public Test_Generator As SwitcherChannel

	Public CardEdge_A As SwitcherChannel
	Public CardEdge_B As SwitcherChannel

	Public Structure SwitcherLocation
		Public Name As String
		Public MuxModule As Integer
		Public Bank As Integer
		Public Channel As Integer

		Public ConnectedMuxModule As Integer
		Public ConnectedBank As Integer
		Public ConnectedChannel As Integer

		Public Sub ConnectChannelToBus()

			If ConnectedMuxModule = MuxModule And ConnectedBank = Bank And ConnectedChannel = Channel Then
				'do nothing
			Else
				'		multiplexoreDACrOUTER.Say("nothing") '("Disconn " & ConnectedMuxModule & ConnectedBank & ConnectedChannel & ",AB" & ConnectedBank)
			End If

			'	multiplexoreDACrOUTER.Say("Connect " & MuxModule & Bank & Channel & ",AB" & Bank)

			'	ConnectedMuxModule = MuxModule
			'	ConnectedBank = Bank
			'	ConnectedChannel = Channel
			'End Sub

			'Public Sub Connect()
			'	multiplexoreDACrOUTER.Say("Connect " & ConnectedMuxModule & ConnectedBank & ConnectedChannel & ",AB" & ConnectedBank)
			'End Sub

			'Public Sub Disconnect()
			'	multiplexoreDACrOUTER.Say("Disconn " & ConnectedMuxModule & ConnectedBank & ConnectedChannel & ",AB" & ConnectedBank)
		End Sub

	End Structure


	Public Structure SwitcherChannel
		Public Left As SwitcherLocation
		Public Right As SwitcherLocation

		Public BusActive As Integer
		Public BusIdle As Integer


		Public Sub ConnectCardToCard()



			'If Left.ConnectedMuxModule = Left.MuxModule And Left.ConnectedBank = Left.Bank And Left.ConnectedChannel = Left.Channel Then
			'	'do nothing
			'Else
			'	multiplexoreDACrOUTER.Say("open " & Left.ConnectedMuxModule & Left.ConnectedBank & Left.ConnectedChannel)
			'End If

			'If Right.ConnectedMuxModule = Right.MuxModule And Right.ConnectedBank = Right.Bank And Right.ConnectedChannel = Right.Channel Then
			'	'do nothing
			'Else
			'	multiplexoreDACrOUTER.Say("open " & Right.ConnectedMuxModule & Right.ConnectedBank & Right.ConnectedChannel)
			'End If

			'multiplexoreDACrOUTER.Say("close 670, 671, 672, " & Left.MuxModule & Left.Bank & Left.Channel & ", " & Right.MuxModule & Right.Bank & Right.Channel)

			Left.ConnectedMuxModule = Left.MuxModule
			Left.ConnectedBank = Left.Bank
			Left.ConnectedChannel = Left.Channel

			Right.ConnectedMuxModule = Right.MuxModule
			Right.ConnectedBank = Right.Bank
			Right.ConnectedChannel = Right.Channel
		End Sub

	End Structure



	Public Sub Multiplexor_Switch_setup()

		multiplexoreDACrOUTER = New BenchInstrumentItem
		multiplexoreDACrOUTER.Name = "Multiplexor"

		multiplexoreDACrOUTER.Address.GPIB_Address = 10
		multiplexoreDACrOUTER.Address.IP = "192.168.0.103"

		multiplexoreDACrOUTER.ConnectToGPIB()
	End Sub

	Private Sub Router_Load(sender As Object, e As EventArgs) Handles MyBase.Load
		Multiplexor_Switch_setup()

	End Sub



	'Private Sub CheckBox_Tone_Left_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Tone_Left.CheckedChanged

	'	If CheckBox_Tone_Left.Checked Then
	'		Multiplexor.Test_Generator.Left.Name = "Left Generator"
	'		Multiplexor.Test_Generator.Left.MuxModule = 7
	'		Multiplexor.Test_Generator.Left.Bank = 0
	'		Multiplexor.Test_Generator.Left.Channel = 1
	'		Multiplexor.Test_Generator.Left.ConnectChannelToBus()
	'	Else
	'		Multiplexor.Test_Generator.Left.Disconnect()
	'	End If



	'End Sub

	'Private Sub CheckBox_Tone_Right_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Tone_Right.CheckedChanged
	'	If CheckBox_Tone_Right.Checked Then
	'		Multiplexor.Test_Generator.Right.Name = "Right Generator"
	'		Multiplexor.Test_Generator.Right.MuxModule = 7
	'		Multiplexor.Test_Generator.Right.Bank = 2
	'		Multiplexor.Test_Generator.Right.Channel = 1
	'		Multiplexor.Test_Generator.Right.ConnectChannelToBus()

	'	Else
	'		Multiplexor.Test_Generator.Right.Disconnect()
	'	End If

	'End Sub


	'Private Sub CheckBox_Dest_Left_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Dest_Left.CheckedChanged

	'	If CheckBox_Dest_Left.Checked Then

	'		Multiplexor.Test_Input.Left.Name = "LEFT Analyzer"
	'		Multiplexor.Test_Input.Left.MuxModule = 7
	'		Multiplexor.Test_Input.Left.Bank = 1
	'		Multiplexor.Test_Input.Left.Channel = 1

	'		Multiplexor.Test_Input.Left.ConnectChannelToBus()
	'	Else
	'		Multiplexor.Test_Input.Left.Disconnect()
	'	End If

	'End Sub

	Private Sub CheckBox_Dest_Right_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Dest_Right.CheckedChanged

		'If CheckBox_Dest_Right.Checked Then
		'	Multiplexor.Test_Input.Right.Name = "RIGHT Analyzer"
		'	Multiplexor.Test_Input.Right.MuxModule = 7
		'	Multiplexor.Test_Input.Right.Bank = 3
		'	Multiplexor.Test_Input.Right.Channel = 1

		'	Multiplexor.Test_Input.Right.ConnectChannelToBus()
		'Else
		'	Multiplexor.Test_Input.Right.Disconnect()
		'End If
	End Sub

	Private Sub ListBox_CardEDAC_A_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ListBox_CardEDAC_A.SelectedIndexChanged

		TrackBar_CardEDAC_A.Value = 23 - ListBox_CardEDAC_A.SelectedIndex
		If CheckBox_EDAC_TIE.Checked Then
			Label_CardEDAC_number_A.Text = SwitcherUpdateEdac(0, TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_A.SelectedIndex)
		Else
			Label_CardEDAC_number_A.Text = SwitcherUpdate(TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_A.SelectedIndex)
		End If

	End Sub

	Private Sub ListBox_CardEDAC_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ListBox_CardEDAC_A.SelectedIndexChanged
		TrackBar_CardEDAC_A.Value = 23 - ListBox_CardEDAC_A.SelectedIndex
		If CheckBox_EDAC_TIE.Checked Then
			Label_CardEDAC_number_A.Text = SwitcherUpdateEdac(0, TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_A.SelectedIndex)
		Else
			Label_CardEDAC_number_A.Text = SwitcherUpdate(TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_A.SelectedIndex)
		End If


	End Sub

	Private Sub ListBox_CardEDAC_B_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ListBox_CardEDAC_B.SelectedIndexChanged
		TrackBar_CardEDAC_B.Value = 23 - ListBox_CardEDAC_B.SelectedIndex
		If CheckBox_EDAC_TIE.Checked Then
			Label_CardEDAC_number_B.Text = SwitcherUpdateEdac(1, TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_B.SelectedIndex)
		Else

			Label_CardEDAC_number_B.Text = SwitcherUpdate(TextBox_CardEDAC_Slot.Text, ListBox_CardEDAC_B.SelectedIndex)
		End If


	End Sub



	'Private Sub TrackBar2_Scroll(sender As Object, e As EventArgs) Handles TrackBar2.Scroll

	'	If TrackBar2.Value < 13 Then
	'		ListBox_Output_1to12.SelectedIndex = TrackBar2.Value - 1
	'		'	ListBox_Output_13to24.SelectedIndex = vbNull

	'		If check_input_output_link.Checked Then
	'			ListBox_Input_1to12.SelectedIndex = ListBox_Output_1to12.SelectedIndex

	'		End If
	'	Else
	'		ListBox_Output_13to24.SelectedIndex = TrackBar2.Value - 13
	'		'ListBox_Output_1to12.SelectedIndex = vbNull
	'		If check_input_output_link.Checked Then
	'			ListBox_Input_13to24.SelectedIndex = ListBox_Output_13to24.SelectedIndex

	'		End If
	'	End If
	'End Sub

	'Private Sub TrackBar1_Scroll(sender As Object, e As EventArgs) Handles TrackBar1.Scroll

	'	If TrackBar1.Value < 13 Then
	'		ListBox_Input_1to12.SelectedIndex = TrackBar1.Value - 1
	'		'ListBox_Input_13to24.SelectedIndex = vbNull
	'		If check_input_output_link.Checked Then
	'			ListBox_Output_1to12.SelectedIndex = ListBox_Input_1to12.SelectedIndex

	'		End If
	'	Else
	'		ListBox_Input_13to24.SelectedIndex = TrackBar1.Value - 13
	'		'ListBox_Input_1to12.SelectedIndex = vbNull

	'		If check_input_output_link.Checked Then
	'			ListBox_Output_13to24.SelectedIndex = ListBox_Input_13to24.SelectedIndex

	'		End If
	'	End If
	'End Sub

	Private Sub ListBox_Input_1to12_SelectedIndexChanged_1(sender As Object, e As EventArgs)

		TrackBar_Input_1to12.Value = 11 - ListBox_Input_1to12.SelectedIndex
		Label_Input_1to12_RelayConnection.Text = SwitcherUpdate(TextBox_Input_1to12_Slot.Text, ListBox_Input_1to12.SelectedIndex + 12)

	End Sub

	Private Sub ListBox_Output_1to12_SelectedIndexChanged_1(sender As Object, e As EventArgs) Handles ListBox_Output_1to12.SelectedIndexChanged
		TrackBar_Output_1to12.Value = 11 - ListBox_Output_1to12.SelectedIndex
		Label_Output_1to12_RelayConnection.Text = SwitcherUpdate(TextBox_Output_1to12_Slot.Text, ListBox_Output_1to12.SelectedIndex)
	End Sub


	Private Sub TrackBar_Output_1to12_Scroll(sender As Object, e As EventArgs) Handles TrackBar_Output_1to12.Scroll
		'Invert Selected Bus
		ListBox_Output_1to12.SelectedIndex = 11 - TrackBar_Output_1to12.Value
		Label_Output_1to12_RelayConnection.Text = SwitcherUpdate(TextBox_Output_1to12_Slot.Text, ListBox_Output_1to12.SelectedIndex)

	End Sub

	Private Sub TrackBar_Input_1to12_Scroll(sender As Object, e As EventArgs)
		ListBox_Input_1to12.SelectedIndex = 11 - TrackBar_Input_1to12.Value
		Label_Input_1to12_RelayConnection.Text = SwitcherUpdate(TextBox_Input_1to12_Slot.Text, ListBox_Input_1to12.SelectedIndex + 12)

	End Sub

	Private Sub TrackBar_Output_13to24_Scroll(sender As Object, e As EventArgs) Handles TrackBar_Output_13to24.Scroll

		ListBox_Output_13to24.SelectedIndex = 11 - TrackBar_Output_13to24.Value
		Label_Output_13to24_RelayConnection.Text = SwitcherUpdate(TextBox_Output_13to24_Slot.Text, ListBox_Output_13to24.SelectedIndex)


	End Sub

	Private Sub ListBox_Output_13to24_SelectedIndexChanged(sender As Object, e As EventArgs) Handles ListBox_Output_13to24.SelectedIndexChanged
		TrackBar_Output_13to24.Value = 11 - ListBox_Output_13to24.SelectedIndex
		Label_Output_13to24_RelayConnection.Text = SwitcherUpdate(TextBox_Output_13to24_Slot.Text, ListBox_Output_13to24.SelectedIndex)

	End Sub

	Private Sub TrackBar_Input_13to24_Scroll(sender As Object, e As EventArgs)
		ListBox_Input_13to24.SelectedIndex = 11 - TrackBar_Input_13to24.Value
		Label_Input_13to24_RelayConnection.Text = SwitcherUpdate(TextBox_Input_13to24_Slot.Text, ListBox_Input_13to24.SelectedIndex + 12)



	End Sub

	Private Sub ListBox_Input_13to24_SelectedIndexChanged(sender As Object, e As EventArgs)
		TrackBar_Input_13to24.Value = 11 - ListBox_Input_13to24.SelectedIndex
		Label_Input_13to24_RelayConnection.Text = SwitcherUpdate(TextBox_Input_13to24_Slot.Text, ListBox_Input_13to24.SelectedIndex + 12)

	End Sub

	Private Sub CheckBox_Tone_Left_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Tone_Left.CheckedChanged

		If CheckBox_Tone_Left.Checked Then
			Test_Generator.Left.Name = "Left Generator"
			Test_Generator.Left.MuxModule = 7
			Test_Generator.Left.Bank = 0
			Test_Generator.Left.Channel = 1
			Test_Generator.Left.ConnectChannelToBus()
		Else
			'Test_Generator.Left.Disconnect()
		End If



	End Sub

	Private Sub CheckBox_Tone_Right_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Tone_Right.CheckedChanged

		If CheckBox_Tone_Right.Checked Then
			Test_Generator.Right.Name = "Right Generator"
			Test_Generator.Right.MuxModule = 7
			Test_Generator.Right.Bank = 2
			Test_Generator.Right.Channel = 1
			Test_Generator.Right.ConnectChannelToBus()

		Else
			'Test_Generator.Right.Disconnect()
		End If


	End Sub


	Public ChannelToRelayLookup(,) As Integer = {{0, 1}, 'OUT,1,L,0,1
	{2, 1}, 'OUT,2,R,2,1
	{0, 2}, 'OUT,3,L,0,2
	{2, 2}, 'OUT,4,R,2,2
	{0, 3}, 'OUT,5,L,0,3
	{2, 3}, 'OUT,6,R,2,3
	{0, 4}, 'OUT,7,L,0,4
	{2, 4}, 'OUT,8,R,2,4
	{0, 5}, 'OUT,9,L,0,5
	{2, 5}, 'OUT,10,R,2,5
	{0, 6}, 'OUT,11,L,0,6
	{2, 6}, 'OUT,12,R,2,6
	{1, 1}, 'IN,1,L,1,1
	{3, 1}, 'IN,2,R,3,1
	{1, 2}, 'IN,3,L,1,2
	{3, 2}, 'IN,4,R,3,2
	{1, 3}, 'IN,5,L,1,3
	{3, 3}, 'IN,6,R,3,3
	{1, 4}, 'IN,7,L,1,4
	{3, 4}, 'IN,8,R,3,4
	{1, 5}, 'IN,9,L,1,5
	{3, 5}, 'IN,10,R,3,5
	{1, 6}, 'IN,11,L,1,6
  {3, 6}}   'IN,12,R,3,6









	Public Function SwitcherUpdate(MuxModule As Integer, Selected As Integer)

		Dim Bank As Integer = ChannelToRelayLookup(Selected, 0)
		Dim Channel As Integer = ChannelToRelayLookup(Selected, 1)

		'if even it is the right channel
		If Bank = 0 Then
			'left
			DUT_input.Left.MuxModule = MuxModule
			DUT_input.Left.Bank = Bank
			DUT_input.Left.Channel = Channel
			DUT_input.BusActive = Bank
			DUT_input.BusIdle = 2

			DUT_input.Left.ConnectChannelToBus()

			'checkbox

			CheckBox_Tone_Left.Checked = True
			CheckBox_Tone_Right.Checked = False
			CheckBox_Music_Left.Checked = True
			CheckBox_Music_Right.Checked = False

		ElseIf Bank = 2 Then
			'right
			DUT_input.Right.MuxModule = MuxModule
			DUT_input.Right.Bank = Bank
			DUT_input.Right.Channel = Channel
			DUT_input.BusActive = Bank
			DUT_input.BusIdle = 0

			DUT_input.Right.ConnectChannelToBus()

			''checkbox
			CheckBox_Tone_Left.Checked = False
			CheckBox_Tone_Right.Checked = True
			CheckBox_Music_Left.Checked = False
			CheckBox_Music_Right.Checked = True


		ElseIf Bank = 1 Then
			'LEFT
			DUT_Output.Left.MuxModule = MuxModule
			DUT_Output.Left.Bank = Bank
			DUT_Output.Left.Channel = Channel

			DUT_Output.Left.ConnectChannelToBus()


			DUT_Output.BusActive = Bank
			DUT_Output.BusIdle = 3

			'checkbox
			CheckBox_Tone_Left.Checked = True
			CheckBox_Tone_Right.Checked = False
			CheckBox_Music_Left.Checked = True
			CheckBox_Music_Right.Checked = False

		ElseIf Bank = 3 Then
			'right
			DUT_Output.Right.MuxModule = MuxModule
			DUT_Output.Right.Bank = Bank
			DUT_Output.Right.Channel = Channel


			DUT_Output.Right.ConnectChannelToBus()

			'checkbox
			''checkbox
			CheckBox_Tone_Left.Checked = False
			CheckBox_Tone_Right.Checked = True
			CheckBox_Music_Left.Checked = False
			CheckBox_Music_Right.Checked = True

			DUT_Output.BusActive = Bank
			DUT_Output.BusIdle = 1


		End If

		Return MuxModule & ChannelToRelayLookup(Selected, 0) & ChannelToRelayLookup(Selected, 1)

	End Function

	Public Function SwitcherUpdateEdac(Location As Boolean, MuxModule As Integer, Selected As Integer)
		Dim Bank As Integer = ChannelToRelayLookup(Selected, 0)
		Dim Channel As Integer = ChannelToRelayLookup(Selected, 1)

		If Location = 0 Then
			CardEdge_A.Left.MuxModule = MuxModule
			CardEdge_A.Left.Bank = Bank
			CardEdge_A.Left.Channel = Channel
		Else

			CardEdge_A.Right.MuxModule = MuxModule
			CardEdge_A.Right.Bank = Bank
			CardEdge_A.Right.Channel = Channel

		End If


		CardEdge_A.ConnectCardToCard()



		Return MuxModule & ChannelToRelayLookup(Selected, 0) & ChannelToRelayLookup(Selected, 1)

	End Function


	Public Sub CheckBoxToggle(BoxNumber As Integer)

		''This Function toggle the checkbox of the found item
		'Dim matches() As Control
		'matches = HP_SWITCHER_V3.Controls.Find(("CheckBox_" & BoxNumber), True)

		'Dim cb As CheckBox = DirectCast(matches(0), CheckBox)

		'If cb.Checked Then
		'	cb.Checked = False
		'Else
		'	cb.Checked = True
		'End If

	End Sub


	Public Sub CheckBoxSet(BoxNumber As Integer, SetAs As Boolean)

		''This Function toggle the checkbox of the found item
		'Dim matches() As Control
		'matches = HP_SWITCHER_V3.Controls.Find(("CheckBox_" & BoxNumber), True)

		'Dim cb As CheckBox = DirectCast(matches(0), CheckBox)


		'cb.Checked = SetAs


	End Sub

	Private Sub TrackBar_Output_SELECT_Scroll(sender As Object, e As EventArgs) Handles TrackBar_Output_SELECT.Scroll

		If TrackBar_Output_SELECT.Value < 13 Then
			ListBox_Output_1to12.SelectedIndex = TrackBar_Output_SELECT.Value - 1
			'	ListBox_Output_13to24.SelectedIndex = vbNull

			If check_input_output_link.Checked Then
				ListBox_Input_1to12.SelectedIndex = ListBox_Output_1to12.SelectedIndex

			End If
		Else
			ListBox_Output_13to24.SelectedIndex = TrackBar_Output_SELECT.Value - 13
			'ListBox_Output_1to12.SelectedIndex = vbNull
			If check_input_output_link.Checked Then
				ListBox_Input_13to24.SelectedIndex = ListBox_Output_13to24.SelectedIndex

			End If
		End If
	End Sub

	Private Sub TrackBar_input_SELECT_Scroll(sender As Object, e As EventArgs) Handles TrackBar_input_SELECT.Scroll


		If TrackBar_input_SELECT.Value < 13 Then
			ListBox_Input_1to12.SelectedIndex = TrackBar_input_SELECT.Value - 1
			'ListBox_Input_13to24.SelectedIndex = vbNull
			If check_input_output_link.Checked Then
				ListBox_Output_1to12.SelectedIndex = ListBox_Input_1to12.SelectedIndex

			End If
		Else
			ListBox_Input_13to24.SelectedIndex = TrackBar_input_SELECT.Value - 13
			'ListBox_Input_1to12.SelectedIndex = vbNull

			If check_input_output_link.Checked Then
				ListBox_Output_13to24.SelectedIndex = ListBox_Input_13to24.SelectedIndex

			End If
		End If
	End Sub

	Private Sub CheckBox_Music_Left_CheckedChanged(sender As Object, e As EventArgs) Handles CheckBox_Music_Left.CheckedChanged

	End Sub





End Class
