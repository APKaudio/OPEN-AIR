<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Router
	Inherits System.Windows.Forms.UserControl

	'UserControl overrides dispose to clean up the component list.
	<System.Diagnostics.DebuggerNonUserCode()> _
	Protected Overrides Sub Dispose(ByVal disposing As Boolean)
		Try
			If disposing AndAlso components IsNot Nothing Then
				components.Dispose()
			End If
		Finally
			MyBase.Dispose(disposing)
		End Try
	End Sub

	'Required by the Windows Form Designer
	Private components As System.ComponentModel.IContainer

	'NOTE: The following procedure is required by the Windows Form Designer
	'It can be modified using the Windows Form Designer.  
	'Do not modify it using the code editor.
	<System.Diagnostics.DebuggerStepThrough()> _
	Private Sub InitializeComponent()
		Dim EDAC_2 As System.Windows.Forms.TabPage
		Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Router))
		Me.GroupBox6 = New System.Windows.Forms.GroupBox()
		Me.Label_Output_13to24_Name = New System.Windows.Forms.Label()
		Me.Label_Input_13to24_RelayConnection = New System.Windows.Forms.Label()
		Me.Label_Output_13to24_RelayConnection = New System.Windows.Forms.Label()
		Me.TextBox_Output_13to24_Slot = New System.Windows.Forms.TextBox()
		Me.ListBox_Output_13to24 = New System.Windows.Forms.ListBox()
		Me.TrackBar_Output_13to24 = New System.Windows.Forms.TrackBar()
		Me.TabControl1 = New System.Windows.Forms.TabControl()
		Me.EDAC_1 = New System.Windows.Forms.TabPage()
		Me.GroupBox1 = New System.Windows.Forms.GroupBox()
		Me.Label_Output_1to12_Name = New System.Windows.Forms.Label()
		Me.Label_Input_1to12_RelayConnection = New System.Windows.Forms.Label()
		Me.TextBox_Output_1to12_Slot = New System.Windows.Forms.TextBox()
		Me.ListBox_Output_1to12 = New System.Windows.Forms.ListBox()
		Me.TrackBar_Output_1to12 = New System.Windows.Forms.TrackBar()
		Me.EDAC_3 = New System.Windows.Forms.TabPage()
		Me.GroupBox4 = New System.Windows.Forms.GroupBox()
		Me.TextBox_CardEDAC_Slot = New System.Windows.Forms.TextBox()
		Me.Label_CardEDAC_RelayConnection = New System.Windows.Forms.Label()
		Me.Label_CardEDAC_number_A = New System.Windows.Forms.Label()
		Me.CheckBox_EDAC_TIE = New System.Windows.Forms.CheckBox()
		Me.ListBox_CardEDAC_A = New System.Windows.Forms.ListBox()
		Me.TrackBar_CardEDAC_A = New System.Windows.Forms.TrackBar()
		Me.Label_CardEDAC_Name = New System.Windows.Forms.Label()
		Me.Busses = New System.Windows.Forms.TabPage()
		Me.GroupBox3 = New System.Windows.Forms.GroupBox()
		Me.TextBox_Bus_Slot = New System.Windows.Forms.TextBox()
		Me.Label_Bus_RelayConnection = New System.Windows.Forms.Label()
		Me.Label_Bus_Number = New System.Windows.Forms.Label()
		Me.ListBox_Bus = New System.Windows.Forms.ListBox()
		Me.TrackBar_Bus = New System.Windows.Forms.TrackBar()
		Me.Label_Bus_Name = New System.Windows.Forms.Label()
		Me.TabControl2 = New System.Windows.Forms.TabControl()
		Me.Tone_and_Music = New System.Windows.Forms.TabPage()
		Me.CheckBox_Tone_Left = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Tone_Right = New System.Windows.Forms.CheckBox()
		Me.check_input_output_link = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Music_Left = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Music_Right = New System.Windows.Forms.CheckBox()
		Me.PictureBox_Output = New System.Windows.Forms.PictureBox()
		Me.TabPage6 = New System.Windows.Forms.TabPage()
		Me.TextBox5 = New System.Windows.Forms.TextBox()
		Me.TextBox6 = New System.Windows.Forms.TextBox()
		Me.TrackBar_Output_SELECT = New System.Windows.Forms.TrackBar()
		Me.OUTPUT_Select = New System.Windows.Forms.TrackBar()
		Me.TextBox1 = New System.Windows.Forms.TextBox()
		Me.TextBox13 = New System.Windows.Forms.TextBox()
		Me.TabControl3 = New System.Windows.Forms.TabControl()
		Me.TabPage1 = New System.Windows.Forms.TabPage()
		Me.PictureBox3 = New System.Windows.Forms.PictureBox()
		Me.PictureBox4 = New System.Windows.Forms.PictureBox()
		Me.CheckBox_Dest_Right = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Monitor_Left = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Dest_Left = New System.Windows.Forms.CheckBox()
		Me.CheckBox_Monitor_Right = New System.Windows.Forms.CheckBox()
		Me.TabPage2 = New System.Windows.Forms.TabPage()
		Me.TextBox2 = New System.Windows.Forms.TextBox()
		Me.TextBox3 = New System.Windows.Forms.TextBox()
		Me.TrackBar_input_SELECT = New System.Windows.Forms.TrackBar()
		Me.TabControl4 = New System.Windows.Forms.TabControl()
		Me.TabPage3 = New System.Windows.Forms.TabPage()
		Me.TextBox_Input_1to12_Slot = New System.Windows.Forms.TextBox()
		Me.Label_Input_1to12_Name = New System.Windows.Forms.Label()
		Me.CheckBox_493 = New System.Windows.Forms.CheckBox()
		Me.CheckBox_491 = New System.Windows.Forms.CheckBox()
		Me.Label_Output_1to12_RelayConnection = New System.Windows.Forms.Label()
		Me.ListBox_Input_1to12 = New System.Windows.Forms.ListBox()
		Me.TrackBar_Input_1to12 = New System.Windows.Forms.TrackBar()
		Me.TabPage4 = New System.Windows.Forms.TabPage()
		Me.TextBox_Input_13to24_Slot = New System.Windows.Forms.TextBox()
		Me.Label_Input_13to24_Name = New System.Windows.Forms.Label()
		Me.CheckBox_593 = New System.Windows.Forms.CheckBox()
		Me.CheckBox_591 = New System.Windows.Forms.CheckBox()
		Me.ListBox_Input_13to24 = New System.Windows.Forms.ListBox()
		Me.TrackBar_Input_13to24 = New System.Windows.Forms.TrackBar()
		Me.TabPage5 = New System.Windows.Forms.TabPage()
		Me.Label_CardEDAC_number_B = New System.Windows.Forms.Label()
		Me.ListBox_CardEDAC_B = New System.Windows.Forms.ListBox()
		Me.TrackBar_CardEDAC_B = New System.Windows.Forms.TrackBar()
		Me.TextBox4 = New System.Windows.Forms.TextBox()
		Me.TrackBar1 = New System.Windows.Forms.TrackBar()
		Me.TrackBar2 = New System.Windows.Forms.TrackBar()
		EDAC_2 = New System.Windows.Forms.TabPage()
		EDAC_2.SuspendLayout()
		Me.GroupBox6.SuspendLayout()
		CType(Me.TrackBar_Output_13to24, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabControl1.SuspendLayout()
		Me.EDAC_1.SuspendLayout()
		Me.GroupBox1.SuspendLayout()
		CType(Me.TrackBar_Output_1to12, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.EDAC_3.SuspendLayout()
		Me.GroupBox4.SuspendLayout()
		CType(Me.TrackBar_CardEDAC_A, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.Busses.SuspendLayout()
		Me.GroupBox3.SuspendLayout()
		CType(Me.TrackBar_Bus, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabControl2.SuspendLayout()
		Me.Tone_and_Music.SuspendLayout()
		CType(Me.PictureBox_Output, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabPage6.SuspendLayout()
		CType(Me.TrackBar_Output_SELECT, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.OUTPUT_Select, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabControl3.SuspendLayout()
		Me.TabPage1.SuspendLayout()
		CType(Me.PictureBox3, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.PictureBox4, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabPage2.SuspendLayout()
		CType(Me.TrackBar_input_SELECT, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabControl4.SuspendLayout()
		Me.TabPage3.SuspendLayout()
		CType(Me.TrackBar_Input_1to12, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabPage4.SuspendLayout()
		CType(Me.TrackBar_Input_13to24, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TabPage5.SuspendLayout()
		CType(Me.TrackBar_CardEDAC_B, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar1, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar2, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.SuspendLayout()
		'
		'EDAC_2
		'
		EDAC_2.Controls.Add(Me.GroupBox6)
		EDAC_2.Cursor = System.Windows.Forms.Cursors.Default
		EDAC_2.Location = New System.Drawing.Point(4, 22)
		EDAC_2.Name = "EDAC_2"
		EDAC_2.Padding = New System.Windows.Forms.Padding(3)
		EDAC_2.Size = New System.Drawing.Size(323, 640)
		EDAC_2.TabIndex = 3
		EDAC_2.Text = "EDAC 2"
		EDAC_2.UseVisualStyleBackColor = True
		'
		'GroupBox6
		'
		Me.GroupBox6.Controls.Add(Me.Label_Output_13to24_Name)
		Me.GroupBox6.Controls.Add(Me.Label_Input_13to24_RelayConnection)
		Me.GroupBox6.Controls.Add(Me.Label_Output_13to24_RelayConnection)
		Me.GroupBox6.Controls.Add(Me.TextBox_Output_13to24_Slot)
		Me.GroupBox6.Controls.Add(Me.ListBox_Output_13to24)
		Me.GroupBox6.Controls.Add(Me.TrackBar_Output_13to24)
		Me.GroupBox6.Cursor = System.Windows.Forms.Cursors.Default
		Me.GroupBox6.Location = New System.Drawing.Point(6, 23)
		Me.GroupBox6.Name = "GroupBox6"
		Me.GroupBox6.Size = New System.Drawing.Size(164, 604)
		Me.GroupBox6.TabIndex = 42
		Me.GroupBox6.TabStop = False
		Me.GroupBox6.Text = "Channel 13-24"
		'
		'Label_Output_13to24_Name
		'
		Me.Label_Output_13to24_Name.AutoSize = True
		Me.Label_Output_13to24_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Output_13to24_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Output_13to24_Name.Location = New System.Drawing.Point(14, 14)
		Me.Label_Output_13to24_Name.Name = "Label_Output_13to24_Name"
		Me.Label_Output_13to24_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_Output_13to24_Name.TabIndex = 27
		Me.Label_Output_13to24_Name.Text = "1"
		Me.Label_Output_13to24_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label_Input_13to24_RelayConnection
		'
		Me.Label_Input_13to24_RelayConnection.AutoSize = True
		Me.Label_Input_13to24_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Input_13to24_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Input_13to24_RelayConnection.Location = New System.Drawing.Point(3, 547)
		Me.Label_Input_13to24_RelayConnection.Name = "Label_Input_13to24_RelayConnection"
		Me.Label_Input_13to24_RelayConnection.Size = New System.Drawing.Size(40, 42)
		Me.Label_Input_13to24_RelayConnection.TabIndex = 26
		Me.Label_Input_13to24_RelayConnection.Text = "1"
		Me.Label_Input_13to24_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label_Output_13to24_RelayConnection
		'
		Me.Label_Output_13to24_RelayConnection.AutoSize = True
		Me.Label_Output_13to24_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Output_13to24_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Output_13to24_RelayConnection.Location = New System.Drawing.Point(11, 216)
		Me.Label_Output_13to24_RelayConnection.Name = "Label_Output_13to24_RelayConnection"
		Me.Label_Output_13to24_RelayConnection.Size = New System.Drawing.Size(40, 42)
		Me.Label_Output_13to24_RelayConnection.TabIndex = 24
		Me.Label_Output_13to24_RelayConnection.Text = "1"
		Me.Label_Output_13to24_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'TextBox_Output_13to24_Slot
		'
		Me.TextBox_Output_13to24_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_Output_13to24_Slot.Location = New System.Drawing.Point(97, 13)
		Me.TextBox_Output_13to24_Slot.Name = "TextBox_Output_13to24_Slot"
		Me.TextBox_Output_13to24_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_Output_13to24_Slot.TabIndex = 16
		Me.TextBox_Output_13to24_Slot.Text = "5"
		'
		'ListBox_Output_13to24
		'
		Me.ListBox_Output_13to24.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_Output_13to24.FormattingEnabled = True
		Me.ListBox_Output_13to24.Items.AddRange(New Object() {"OUT,13,L,0,1", "OUT,14,R,2,1", "OUT,15,L,0,2", "OUT,16,R,2,2", "OUT,17,L,0,3", "OUT,18,R,2,3", "OUT,19,L,0,4", "OUT,20,R,2,4", "OUT,21,L,0,5", "OUT,22,R,2,5", "OUT,23,L,0,6", "OUT,24,R,2,6"})
		Me.ListBox_Output_13to24.Location = New System.Drawing.Point(38, 48)
		Me.ListBox_Output_13to24.Name = "ListBox_Output_13to24"
		Me.ListBox_Output_13to24.Size = New System.Drawing.Size(80, 160)
		Me.ListBox_Output_13to24.TabIndex = 20
		'
		'TrackBar_Output_13to24
		'
		Me.TrackBar_Output_13to24.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(0, Byte), Integer))
		Me.TrackBar_Output_13to24.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Output_13to24.LargeChange = 1
		Me.TrackBar_Output_13to24.Location = New System.Drawing.Point(9, 42)
		Me.TrackBar_Output_13to24.Maximum = 11
		Me.TrackBar_Output_13to24.Name = "TrackBar_Output_13to24"
		Me.TrackBar_Output_13to24.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_Output_13to24.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_Output_13to24.Size = New System.Drawing.Size(45, 171)
		Me.TrackBar_Output_13to24.TabIndex = 19
		Me.TrackBar_Output_13to24.Value = 1
		'
		'TabControl1
		'
		Me.TabControl1.Controls.Add(Me.EDAC_1)
		Me.TabControl1.Controls.Add(EDAC_2)
		Me.TabControl1.Controls.Add(Me.EDAC_3)
		Me.TabControl1.Controls.Add(Me.Busses)
		Me.TabControl1.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabControl1.Location = New System.Drawing.Point(10, 201)
		Me.TabControl1.Name = "TabControl1"
		Me.TabControl1.SelectedIndex = 0
		Me.TabControl1.Size = New System.Drawing.Size(331, 666)
		Me.TabControl1.TabIndex = 223
		'
		'EDAC_1
		'
		Me.EDAC_1.Controls.Add(Me.GroupBox1)
		Me.EDAC_1.Cursor = System.Windows.Forms.Cursors.Default
		Me.EDAC_1.Location = New System.Drawing.Point(4, 22)
		Me.EDAC_1.Name = "EDAC_1"
		Me.EDAC_1.Padding = New System.Windows.Forms.Padding(3)
		Me.EDAC_1.Size = New System.Drawing.Size(323, 640)
		Me.EDAC_1.TabIndex = 0
		Me.EDAC_1.Text = "EDAC_1"
		Me.EDAC_1.UseVisualStyleBackColor = True
		'
		'GroupBox1
		'
		Me.GroupBox1.Controls.Add(Me.Label_Output_1to12_Name)
		Me.GroupBox1.Controls.Add(Me.Label_Input_1to12_RelayConnection)
		Me.GroupBox1.Controls.Add(Me.TextBox_Output_1to12_Slot)
		Me.GroupBox1.Controls.Add(Me.ListBox_Output_1to12)
		Me.GroupBox1.Controls.Add(Me.TrackBar_Output_1to12)
		Me.GroupBox1.Cursor = System.Windows.Forms.Cursors.Default
		Me.GroupBox1.Location = New System.Drawing.Point(6, 6)
		Me.GroupBox1.Name = "GroupBox1"
		Me.GroupBox1.Size = New System.Drawing.Size(183, 606)
		Me.GroupBox1.TabIndex = 40
		Me.GroupBox1.TabStop = False
		Me.GroupBox1.Text = "Channel 1-12"
		'
		'Label_Output_1to12_Name
		'
		Me.Label_Output_1to12_Name.AutoSize = True
		Me.Label_Output_1to12_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Output_1to12_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Output_1to12_Name.Location = New System.Drawing.Point(6, 14)
		Me.Label_Output_1to12_Name.Name = "Label_Output_1to12_Name"
		Me.Label_Output_1to12_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_Output_1to12_Name.TabIndex = 23
		Me.Label_Output_1to12_Name.Text = "1"
		Me.Label_Output_1to12_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label_Input_1to12_RelayConnection
		'
		Me.Label_Input_1to12_RelayConnection.AutoSize = True
		Me.Label_Input_1to12_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Input_1to12_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Input_1to12_RelayConnection.Location = New System.Drawing.Point(11, 545)
		Me.Label_Input_1to12_RelayConnection.Name = "Label_Input_1to12_RelayConnection"
		Me.Label_Input_1to12_RelayConnection.Size = New System.Drawing.Size(40, 42)
		Me.Label_Input_1to12_RelayConnection.TabIndex = 22
		Me.Label_Input_1to12_RelayConnection.Text = "1"
		Me.Label_Input_1to12_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'TextBox_Output_1to12_Slot
		'
		Me.TextBox_Output_1to12_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_Output_1to12_Slot.Location = New System.Drawing.Point(97, 19)
		Me.TextBox_Output_1to12_Slot.Name = "TextBox_Output_1to12_Slot"
		Me.TextBox_Output_1to12_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_Output_1to12_Slot.TabIndex = 16
		Me.TextBox_Output_1to12_Slot.Text = "4"
		'
		'ListBox_Output_1to12
		'
		Me.ListBox_Output_1to12.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_Output_1to12.FormattingEnabled = True
		Me.ListBox_Output_1to12.Items.AddRange(New Object() {"OUT,1,L,0,1", "OUT,2,R,2,1", "OUT,3,L,0,2", "OUT,4,R,2,2", "OUT,5,L,0,3", "OUT,6,R,2,3", "OUT,7,L,0,4", "OUT,8,R,2,4", "OUT,9,L,0,5", "OUT,10,R,2,5", "OUT,11,L,0,6", "OUT,12,R,2,6"})
		Me.ListBox_Output_1to12.Location = New System.Drawing.Point(38, 50)
		Me.ListBox_Output_1to12.Name = "ListBox_Output_1to12"
		Me.ListBox_Output_1to12.Size = New System.Drawing.Size(88, 160)
		Me.ListBox_Output_1to12.TabIndex = 13
		'
		'TrackBar_Output_1to12
		'
		Me.TrackBar_Output_1to12.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(0, Byte), Integer))
		Me.TrackBar_Output_1to12.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Output_1to12.LargeChange = 1
		Me.TrackBar_Output_1to12.Location = New System.Drawing.Point(9, 44)
		Me.TrackBar_Output_1to12.Maximum = 11
		Me.TrackBar_Output_1to12.Name = "TrackBar_Output_1to12"
		Me.TrackBar_Output_1to12.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_Output_1to12.RightToLeft = System.Windows.Forms.RightToLeft.No
		Me.TrackBar_Output_1to12.Size = New System.Drawing.Size(45, 171)
		Me.TrackBar_Output_1to12.TabIndex = 10
		Me.TrackBar_Output_1to12.Value = 1
		'
		'EDAC_3
		'
		Me.EDAC_3.Controls.Add(Me.GroupBox4)
		Me.EDAC_3.Cursor = System.Windows.Forms.Cursors.Default
		Me.EDAC_3.Location = New System.Drawing.Point(4, 22)
		Me.EDAC_3.Name = "EDAC_3"
		Me.EDAC_3.Padding = New System.Windows.Forms.Padding(3)
		Me.EDAC_3.Size = New System.Drawing.Size(323, 640)
		Me.EDAC_3.TabIndex = 1
		Me.EDAC_3.Text = "EDAC 3"
		Me.EDAC_3.UseVisualStyleBackColor = True
		'
		'GroupBox4
		'
		Me.GroupBox4.Controls.Add(Me.TextBox_CardEDAC_Slot)
		Me.GroupBox4.Controls.Add(Me.Label_CardEDAC_RelayConnection)
		Me.GroupBox4.Controls.Add(Me.Label_CardEDAC_number_A)
		Me.GroupBox4.Controls.Add(Me.CheckBox_EDAC_TIE)
		Me.GroupBox4.Controls.Add(Me.ListBox_CardEDAC_A)
		Me.GroupBox4.Controls.Add(Me.TrackBar_CardEDAC_A)
		Me.GroupBox4.Controls.Add(Me.Label_CardEDAC_Name)
		Me.GroupBox4.Cursor = System.Windows.Forms.Cursors.Default
		Me.GroupBox4.Location = New System.Drawing.Point(7, 23)
		Me.GroupBox4.Name = "GroupBox4"
		Me.GroupBox4.Size = New System.Drawing.Size(201, 525)
		Me.GroupBox4.TabIndex = 221
		Me.GroupBox4.TabStop = False
		Me.GroupBox4.Text = "Card EDAC"
		'
		'TextBox_CardEDAC_Slot
		'
		Me.TextBox_CardEDAC_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_CardEDAC_Slot.Location = New System.Drawing.Point(83, 16)
		Me.TextBox_CardEDAC_Slot.Name = "TextBox_CardEDAC_Slot"
		Me.TextBox_CardEDAC_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_CardEDAC_Slot.TabIndex = 16
		Me.TextBox_CardEDAC_Slot.Text = "6"
		'
		'Label_CardEDAC_RelayConnection
		'
		Me.Label_CardEDAC_RelayConnection.AutoSize = True
		Me.Label_CardEDAC_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_CardEDAC_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_CardEDAC_RelayConnection.Location = New System.Drawing.Point(6, 489)
		Me.Label_CardEDAC_RelayConnection.Name = "Label_CardEDAC_RelayConnection"
		Me.Label_CardEDAC_RelayConnection.Size = New System.Drawing.Size(40, 42)
		Me.Label_CardEDAC_RelayConnection.TabIndex = 15
		Me.Label_CardEDAC_RelayConnection.Text = "1"
		Me.Label_CardEDAC_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label_CardEDAC_number_A
		'
		Me.Label_CardEDAC_number_A.AutoSize = True
		Me.Label_CardEDAC_number_A.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_CardEDAC_number_A.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_CardEDAC_number_A.Location = New System.Drawing.Point(12, 388)
		Me.Label_CardEDAC_number_A.Name = "Label_CardEDAC_number_A"
		Me.Label_CardEDAC_number_A.Size = New System.Drawing.Size(40, 42)
		Me.Label_CardEDAC_number_A.TabIndex = 14
		Me.Label_CardEDAC_number_A.Text = "1"
		Me.Label_CardEDAC_number_A.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'CheckBox_EDAC_TIE
		'
		Me.CheckBox_EDAC_TIE.AutoSize = True
		Me.CheckBox_EDAC_TIE.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_EDAC_TIE.Location = New System.Drawing.Point(72, 538)
		Me.CheckBox_EDAC_TIE.Name = "CheckBox_EDAC_TIE"
		Me.CheckBox_EDAC_TIE.Size = New System.Drawing.Size(44, 17)
		Me.CheckBox_EDAC_TIE.TabIndex = 54
		Me.CheckBox_EDAC_TIE.Text = "691"
		Me.CheckBox_EDAC_TIE.UseVisualStyleBackColor = True
		'
		'ListBox_CardEDAC_A
		'
		Me.ListBox_CardEDAC_A.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_CardEDAC_A.FormattingEnabled = True
		Me.ListBox_CardEDAC_A.Items.AddRange(New Object() {"A-1", "B-2", "C-3", "D-4", "E-5", "F-6", "H-7", "J-8", "K-9", "L-10", "M-11", "N-12", "P-13", "R-14", "S-15", "T-16", "U-17", "V-18", "W-19", "X-20", "Y-21", "Z-22", "NC", "NC"})
		Me.ListBox_CardEDAC_A.Location = New System.Drawing.Point(44, 57)
		Me.ListBox_CardEDAC_A.Name = "ListBox_CardEDAC_A"
		Me.ListBox_CardEDAC_A.Size = New System.Drawing.Size(41, 316)
		Me.ListBox_CardEDAC_A.TabIndex = 13
		'
		'TrackBar_CardEDAC_A
		'
		Me.TrackBar_CardEDAC_A.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(0, Byte), Integer))
		Me.TrackBar_CardEDAC_A.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_CardEDAC_A.LargeChange = 1
		Me.TrackBar_CardEDAC_A.Location = New System.Drawing.Point(15, 51)
		Me.TrackBar_CardEDAC_A.Maximum = 23
		Me.TrackBar_CardEDAC_A.Name = "TrackBar_CardEDAC_A"
		Me.TrackBar_CardEDAC_A.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_CardEDAC_A.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_CardEDAC_A.Size = New System.Drawing.Size(45, 328)
		Me.TrackBar_CardEDAC_A.TabIndex = 10
		Me.TrackBar_CardEDAC_A.Value = 1
		'
		'Label_CardEDAC_Name
		'
		Me.Label_CardEDAC_Name.AutoSize = True
		Me.Label_CardEDAC_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_CardEDAC_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_CardEDAC_Name.Location = New System.Drawing.Point(10, 18)
		Me.Label_CardEDAC_Name.Name = "Label_CardEDAC_Name"
		Me.Label_CardEDAC_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_CardEDAC_Name.TabIndex = 12
		Me.Label_CardEDAC_Name.Text = "1"
		Me.Label_CardEDAC_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Busses
		'
		Me.Busses.Controls.Add(Me.GroupBox3)
		Me.Busses.Cursor = System.Windows.Forms.Cursors.Default
		Me.Busses.Location = New System.Drawing.Point(4, 22)
		Me.Busses.Name = "Busses"
		Me.Busses.Padding = New System.Windows.Forms.Padding(3)
		Me.Busses.Size = New System.Drawing.Size(323, 640)
		Me.Busses.TabIndex = 2
		Me.Busses.Text = "Busses"
		Me.Busses.UseVisualStyleBackColor = True
		'
		'GroupBox3
		'
		Me.GroupBox3.Controls.Add(Me.TextBox_Bus_Slot)
		Me.GroupBox3.Controls.Add(Me.Label_Bus_RelayConnection)
		Me.GroupBox3.Controls.Add(Me.Label_Bus_Number)
		Me.GroupBox3.Controls.Add(Me.ListBox_Bus)
		Me.GroupBox3.Controls.Add(Me.TrackBar_Bus)
		Me.GroupBox3.Controls.Add(Me.Label_Bus_Name)
		Me.GroupBox3.Cursor = System.Windows.Forms.Cursors.Default
		Me.GroupBox3.Location = New System.Drawing.Point(6, 6)
		Me.GroupBox3.Name = "GroupBox3"
		Me.GroupBox3.Size = New System.Drawing.Size(183, 547)
		Me.GroupBox3.TabIndex = 220
		Me.GroupBox3.TabStop = False
		Me.GroupBox3.Text = "Busses"
		'
		'TextBox_Bus_Slot
		'
		Me.TextBox_Bus_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_Bus_Slot.Location = New System.Drawing.Point(100, 26)
		Me.TextBox_Bus_Slot.Name = "TextBox_Bus_Slot"
		Me.TextBox_Bus_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_Bus_Slot.TabIndex = 17
		Me.TextBox_Bus_Slot.Text = "700"
		'
		'Label_Bus_RelayConnection
		'
		Me.Label_Bus_RelayConnection.AutoSize = True
		Me.Label_Bus_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Bus_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Bus_RelayConnection.Location = New System.Drawing.Point(73, 426)
		Me.Label_Bus_RelayConnection.Name = "Label_Bus_RelayConnection"
		Me.Label_Bus_RelayConnection.Size = New System.Drawing.Size(40, 42)
		Me.Label_Bus_RelayConnection.TabIndex = 15
		Me.Label_Bus_RelayConnection.Text = "1"
		Me.Label_Bus_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'Label_Bus_Number
		'
		Me.Label_Bus_Number.AutoSize = True
		Me.Label_Bus_Number.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Bus_Number.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Bus_Number.Location = New System.Drawing.Point(9, 398)
		Me.Label_Bus_Number.Name = "Label_Bus_Number"
		Me.Label_Bus_Number.Size = New System.Drawing.Size(40, 42)
		Me.Label_Bus_Number.TabIndex = 14
		Me.Label_Bus_Number.Text = "1"
		Me.Label_Bus_Number.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'ListBox_Bus
		'
		Me.ListBox_Bus.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_Bus.FormattingEnabled = True
		Me.ListBox_Bus.Items.AddRange(New Object() {"M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "Aux 1", "Aux 2 ", "Aux 3", "Aux 4", "Aux 5", "Aux 6", "Aux 7", "Aux 8", "Monitor 1", "Monitor 2", "Monitor 3", "Monitor 4", "Monitor 5", "Monitor 6 - ", "Monitor 7 - PFL", "Monitor 8 - SOLO"})
		Me.ListBox_Bus.Location = New System.Drawing.Point(41, 67)
		Me.ListBox_Bus.Name = "ListBox_Bus"
		Me.ListBox_Bus.Size = New System.Drawing.Size(120, 316)
		Me.ListBox_Bus.TabIndex = 13
		'
		'TrackBar_Bus
		'
		Me.TrackBar_Bus.BackColor = System.Drawing.Color.Lime
		Me.TrackBar_Bus.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Bus.LargeChange = 1
		Me.TrackBar_Bus.Location = New System.Drawing.Point(12, 61)
		Me.TrackBar_Bus.Maximum = 23
		Me.TrackBar_Bus.Name = "TrackBar_Bus"
		Me.TrackBar_Bus.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_Bus.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_Bus.Size = New System.Drawing.Size(45, 328)
		Me.TrackBar_Bus.TabIndex = 10
		Me.TrackBar_Bus.Value = 1
		'
		'Label_Bus_Name
		'
		Me.Label_Bus_Name.AutoSize = True
		Me.Label_Bus_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Bus_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Bus_Name.Location = New System.Drawing.Point(4, 22)
		Me.Label_Bus_Name.Name = "Label_Bus_Name"
		Me.Label_Bus_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_Bus_Name.TabIndex = 12
		Me.Label_Bus_Name.Text = "1"
		Me.Label_Bus_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'TabControl2
		'
		Me.TabControl2.Controls.Add(Me.Tone_and_Music)
		Me.TabControl2.Controls.Add(Me.TabPage6)
		Me.TabControl2.Cursor = System.Windows.Forms.Cursors.Arrow
		Me.TabControl2.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.TabControl2.Location = New System.Drawing.Point(0, 8)
		Me.TabControl2.Name = "TabControl2"
		Me.TabControl2.SelectedIndex = 0
		Me.TabControl2.Size = New System.Drawing.Size(358, 169)
		Me.TabControl2.TabIndex = 222
		'
		'Tone_and_Music
		'
		Me.Tone_and_Music.Controls.Add(Me.CheckBox_Tone_Left)
		Me.Tone_and_Music.Controls.Add(Me.CheckBox_Tone_Right)
		Me.Tone_and_Music.Controls.Add(Me.check_input_output_link)
		Me.Tone_and_Music.Controls.Add(Me.CheckBox_Music_Left)
		Me.Tone_and_Music.Controls.Add(Me.CheckBox_Music_Right)
		Me.Tone_and_Music.Controls.Add(Me.PictureBox_Output)
		Me.Tone_and_Music.Cursor = System.Windows.Forms.Cursors.Default
		Me.Tone_and_Music.Location = New System.Drawing.Point(4, 24)
		Me.Tone_and_Music.Name = "Tone_and_Music"
		Me.Tone_and_Music.Padding = New System.Windows.Forms.Padding(3)
		Me.Tone_and_Music.Size = New System.Drawing.Size(350, 141)
		Me.Tone_and_Music.TabIndex = 1
		Me.Tone_and_Music.Text = "Tone and Music"
		Me.Tone_and_Music.UseVisualStyleBackColor = True
		'
		'CheckBox_Tone_Left
		'
		Me.CheckBox_Tone_Left.AutoSize = True
		Me.CheckBox_Tone_Left.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Tone_Left.Location = New System.Drawing.Point(95, 62)
		Me.CheckBox_Tone_Left.Name = "CheckBox_Tone_Left"
		Me.CheckBox_Tone_Left.Size = New System.Drawing.Size(80, 19)
		Me.CheckBox_Tone_Left.TabIndex = 0
		Me.CheckBox_Tone_Left.Text = "Tone  Left"
		Me.CheckBox_Tone_Left.UseVisualStyleBackColor = True
		'
		'CheckBox_Tone_Right
		'
		Me.CheckBox_Tone_Right.AutoSize = True
		Me.CheckBox_Tone_Right.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Tone_Right.Location = New System.Drawing.Point(117, 86)
		Me.CheckBox_Tone_Right.Name = "CheckBox_Tone_Right"
		Me.CheckBox_Tone_Right.Size = New System.Drawing.Size(86, 19)
		Me.CheckBox_Tone_Right.TabIndex = 1
		Me.CheckBox_Tone_Right.Text = "Tone Right"
		Me.CheckBox_Tone_Right.UseVisualStyleBackColor = True
		'
		'check_input_output_link
		'
		Me.check_input_output_link.AutoSize = True
		Me.check_input_output_link.Checked = True
		Me.check_input_output_link.CheckState = System.Windows.Forms.CheckState.Checked
		Me.check_input_output_link.Cursor = System.Windows.Forms.Cursors.Default
		Me.check_input_output_link.Location = New System.Drawing.Point(9, 102)
		Me.check_input_output_link.Name = "check_input_output_link"
		Me.check_input_output_link.Size = New System.Drawing.Size(58, 19)
		Me.check_input_output_link.TabIndex = 2
		Me.check_input_output_link.Text = "Mono"
		Me.check_input_output_link.UseVisualStyleBackColor = True
		'
		'CheckBox_Music_Left
		'
		Me.CheckBox_Music_Left.AutoSize = True
		Me.CheckBox_Music_Left.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Music_Left.Location = New System.Drawing.Point(83, 7)
		Me.CheckBox_Music_Left.Name = "CheckBox_Music_Left"
		Me.CheckBox_Music_Left.Size = New System.Drawing.Size(124, 19)
		Me.CheckBox_Music_Left.TabIndex = 0
		Me.CheckBox_Music_Left.Text = "Music Source Left"
		Me.CheckBox_Music_Left.UseVisualStyleBackColor = True
		'
		'CheckBox_Music_Right
		'
		Me.CheckBox_Music_Right.AutoSize = True
		Me.CheckBox_Music_Right.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Music_Right.Location = New System.Drawing.Point(109, 33)
		Me.CheckBox_Music_Right.Name = "CheckBox_Music_Right"
		Me.CheckBox_Music_Right.Size = New System.Drawing.Size(133, 19)
		Me.CheckBox_Music_Right.TabIndex = 1
		Me.CheckBox_Music_Right.Text = "Music Source Right"
		Me.CheckBox_Music_Right.UseVisualStyleBackColor = True
		'
		'PictureBox_Output
		'
		Me.PictureBox_Output.Cursor = System.Windows.Forms.Cursors.Default
		Me.PictureBox_Output.Image = CType(resources.GetObject("PictureBox_Output.Image"), System.Drawing.Image)
		Me.PictureBox_Output.Location = New System.Drawing.Point(-1, 7)
		Me.PictureBox_Output.Name = "PictureBox_Output"
		Me.PictureBox_Output.Size = New System.Drawing.Size(81, 89)
		Me.PictureBox_Output.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
		Me.PictureBox_Output.TabIndex = 74
		Me.PictureBox_Output.TabStop = False
		'
		'TabPage6
		'
		Me.TabPage6.Controls.Add(Me.TextBox5)
		Me.TabPage6.Controls.Add(Me.TextBox6)
		Me.TabPage6.Controls.Add(Me.TrackBar_Output_SELECT)
		Me.TabPage6.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage6.Location = New System.Drawing.Point(4, 24)
		Me.TabPage6.Name = "TabPage6"
		Me.TabPage6.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage6.Size = New System.Drawing.Size(350, 141)
		Me.TabPage6.TabIndex = 2
		Me.TabPage6.Text = "TabPage6"
		Me.TabPage6.UseVisualStyleBackColor = True
		'
		'TextBox5
		'
		Me.TextBox5.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox5.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox5.Location = New System.Drawing.Point(15, 9)
		Me.TextBox5.Name = "TextBox5"
		Me.TextBox5.Size = New System.Drawing.Size(115, 30)
		Me.TextBox5.TabIndex = 263
		Me.TextBox5.Text = "From Pool Left"
		'
		'TextBox6
		'
		Me.TextBox6.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox6.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox6.Location = New System.Drawing.Point(137, 9)
		Me.TextBox6.Name = "TextBox6"
		Me.TextBox6.Size = New System.Drawing.Size(125, 30)
		Me.TextBox6.TabIndex = 264
		Me.TextBox6.Text = "From Pool Right"
		'
		'TrackBar_Output_SELECT
		'
		Me.TrackBar_Output_SELECT.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Output_SELECT.Location = New System.Drawing.Point(6, 74)
		Me.TrackBar_Output_SELECT.Maximum = 24
		Me.TrackBar_Output_SELECT.Minimum = 1
		Me.TrackBar_Output_SELECT.Name = "TrackBar_Output_SELECT"
		Me.TrackBar_Output_SELECT.Size = New System.Drawing.Size(277, 45)
		Me.TrackBar_Output_SELECT.TabIndex = 261
		Me.TrackBar_Output_SELECT.Value = 1
		'
		'OUTPUT_Select
		'
		Me.OUTPUT_Select.Cursor = System.Windows.Forms.Cursors.Default
		Me.OUTPUT_Select.Location = New System.Drawing.Point(0, 0)
		Me.OUTPUT_Select.Name = "OUTPUT_Select"
		Me.OUTPUT_Select.Size = New System.Drawing.Size(104, 45)
		Me.OUTPUT_Select.TabIndex = 0
		'
		'TextBox1
		'
		Me.TextBox1.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox1.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox1.Location = New System.Drawing.Point(6, 6)
		Me.TextBox1.Name = "TextBox1"
		Me.TextBox1.Size = New System.Drawing.Size(167, 30)
		Me.TextBox1.TabIndex = 38
		Me.TextBox1.Text = "From Pool Left"
		'
		'TextBox13
		'
		Me.TextBox13.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox13.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox13.Location = New System.Drawing.Point(177, 6)
		Me.TextBox13.Name = "TextBox13"
		Me.TextBox13.Size = New System.Drawing.Size(154, 30)
		Me.TextBox13.TabIndex = 50
		Me.TextBox13.Text = "From Pool Right"
		'
		'TabControl3
		'
		Me.TabControl3.Controls.Add(Me.TabPage1)
		Me.TabControl3.Controls.Add(Me.TabPage2)
		Me.TabControl3.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabControl3.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.TabControl3.Location = New System.Drawing.Point(359, 8)
		Me.TabControl3.Name = "TabControl3"
		Me.TabControl3.SelectedIndex = 0
		Me.TabControl3.Size = New System.Drawing.Size(336, 191)
		Me.TabControl3.TabIndex = 224
		'
		'TabPage1
		'
		Me.TabPage1.Controls.Add(Me.PictureBox3)
		Me.TabPage1.Controls.Add(Me.PictureBox4)
		Me.TabPage1.Controls.Add(Me.CheckBox_Dest_Right)
		Me.TabPage1.Controls.Add(Me.CheckBox_Monitor_Left)
		Me.TabPage1.Controls.Add(Me.CheckBox_Dest_Left)
		Me.TabPage1.Controls.Add(Me.CheckBox_Monitor_Right)
		Me.TabPage1.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage1.Location = New System.Drawing.Point(4, 29)
		Me.TabPage1.Name = "TabPage1"
		Me.TabPage1.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage1.Size = New System.Drawing.Size(328, 158)
		Me.TabPage1.TabIndex = 0
		Me.TabPage1.Text = "TabPage1"
		Me.TabPage1.UseVisualStyleBackColor = True
		'
		'PictureBox3
		'
		Me.PictureBox3.Cursor = System.Windows.Forms.Cursors.Default
		Me.PictureBox3.Image = CType(resources.GetObject("PictureBox3.Image"), System.Drawing.Image)
		Me.PictureBox3.Location = New System.Drawing.Point(164, 66)
		Me.PictureBox3.Name = "PictureBox3"
		Me.PictureBox3.Size = New System.Drawing.Size(53, 53)
		Me.PictureBox3.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
		Me.PictureBox3.TabIndex = 255
		Me.PictureBox3.TabStop = False
		'
		'PictureBox4
		'
		Me.PictureBox4.Cursor = System.Windows.Forms.Cursors.Default
		Me.PictureBox4.Image = CType(resources.GetObject("PictureBox4.Image"), System.Drawing.Image)
		Me.PictureBox4.Location = New System.Drawing.Point(244, 67)
		Me.PictureBox4.Name = "PictureBox4"
		Me.PictureBox4.Size = New System.Drawing.Size(53, 53)
		Me.PictureBox4.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom
		Me.PictureBox4.TabIndex = 254
		Me.PictureBox4.TabStop = False
		'
		'CheckBox_Dest_Right
		'
		Me.CheckBox_Dest_Right.AutoSize = True
		Me.CheckBox_Dest_Right.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Dest_Right.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.CheckBox_Dest_Right.Location = New System.Drawing.Point(76, 28)
		Me.CheckBox_Dest_Right.Name = "CheckBox_Dest_Right"
		Me.CheckBox_Dest_Right.Size = New System.Drawing.Size(120, 19)
		Me.CheckBox_Dest_Right.TabIndex = 184
		Me.CheckBox_Dest_Right.Text = "Destination Right"
		Me.CheckBox_Dest_Right.UseVisualStyleBackColor = True
		'
		'CheckBox_Monitor_Left
		'
		Me.CheckBox_Monitor_Left.AutoSize = True
		Me.CheckBox_Monitor_Left.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Monitor_Left.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.CheckBox_Monitor_Left.Location = New System.Drawing.Point(206, 2)
		Me.CheckBox_Monitor_Left.Name = "CheckBox_Monitor_Left"
		Me.CheckBox_Monitor_Left.Size = New System.Drawing.Size(91, 19)
		Me.CheckBox_Monitor_Left.TabIndex = 185
		Me.CheckBox_Monitor_Left.Text = "Monitor Left"
		Me.CheckBox_Monitor_Left.UseVisualStyleBackColor = True
		'
		'CheckBox_Dest_Left
		'
		Me.CheckBox_Dest_Left.AutoSize = True
		Me.CheckBox_Dest_Left.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Dest_Left.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.CheckBox_Dest_Left.Location = New System.Drawing.Point(76, 6)
		Me.CheckBox_Dest_Left.Name = "CheckBox_Dest_Left"
		Me.CheckBox_Dest_Left.Size = New System.Drawing.Size(111, 19)
		Me.CheckBox_Dest_Left.TabIndex = 183
		Me.CheckBox_Dest_Left.Text = "Destination Left"
		Me.CheckBox_Dest_Left.UseVisualStyleBackColor = True
		'
		'CheckBox_Monitor_Right
		'
		Me.CheckBox_Monitor_Right.AutoSize = True
		Me.CheckBox_Monitor_Right.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_Monitor_Right.Font = New System.Drawing.Font("Microsoft Sans Serif", 9.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.CheckBox_Monitor_Right.Location = New System.Drawing.Point(200, 26)
		Me.CheckBox_Monitor_Right.Name = "CheckBox_Monitor_Right"
		Me.CheckBox_Monitor_Right.Size = New System.Drawing.Size(100, 19)
		Me.CheckBox_Monitor_Right.TabIndex = 186
		Me.CheckBox_Monitor_Right.Text = "Monitor Right"
		Me.CheckBox_Monitor_Right.UseVisualStyleBackColor = True
		'
		'TabPage2
		'
		Me.TabPage2.Controls.Add(Me.TextBox2)
		Me.TabPage2.Controls.Add(Me.TextBox3)
		Me.TabPage2.Controls.Add(Me.TrackBar_input_SELECT)
		Me.TabPage2.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage2.Location = New System.Drawing.Point(4, 29)
		Me.TabPage2.Name = "TabPage2"
		Me.TabPage2.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage2.Size = New System.Drawing.Size(328, 158)
		Me.TabPage2.TabIndex = 1
		Me.TabPage2.Text = "TabPage2"
		Me.TabPage2.UseVisualStyleBackColor = True
		'
		'TextBox2
		'
		Me.TextBox2.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox2.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox2.Location = New System.Drawing.Point(6, 12)
		Me.TextBox2.Name = "TextBox2"
		Me.TextBox2.Size = New System.Drawing.Size(115, 30)
		Me.TextBox2.TabIndex = 255
		Me.TextBox2.Text = "From Pool Left"
		'
		'TextBox3
		'
		Me.TextBox3.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox3.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.0!)
		Me.TextBox3.Location = New System.Drawing.Point(128, 12)
		Me.TextBox3.Name = "TextBox3"
		Me.TextBox3.Size = New System.Drawing.Size(125, 30)
		Me.TextBox3.TabIndex = 256
		Me.TextBox3.Text = "From Pool Right"
		'
		'TrackBar_input_SELECT
		'
		Me.TrackBar_input_SELECT.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_input_SELECT.Location = New System.Drawing.Point(15, 71)
		Me.TrackBar_input_SELECT.Maximum = 24
		Me.TrackBar_input_SELECT.Minimum = 1
		Me.TrackBar_input_SELECT.Name = "TrackBar_input_SELECT"
		Me.TrackBar_input_SELECT.Size = New System.Drawing.Size(277, 45)
		Me.TrackBar_input_SELECT.TabIndex = 188
		Me.TrackBar_input_SELECT.Value = 1
		'
		'TabControl4
		'
		Me.TabControl4.Controls.Add(Me.TabPage3)
		Me.TabControl4.Controls.Add(Me.TabPage4)
		Me.TabControl4.Controls.Add(Me.TabPage5)
		Me.TabControl4.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabControl4.Location = New System.Drawing.Point(359, 228)
		Me.TabControl4.Name = "TabControl4"
		Me.TabControl4.SelectedIndex = 0
		Me.TabControl4.Size = New System.Drawing.Size(277, 469)
		Me.TabControl4.TabIndex = 225
		'
		'TabPage3
		'
		Me.TabPage3.Controls.Add(Me.TextBox_Input_1to12_Slot)
		Me.TabPage3.Controls.Add(Me.Label_Input_1to12_Name)
		Me.TabPage3.Controls.Add(Me.CheckBox_493)
		Me.TabPage3.Controls.Add(Me.CheckBox_491)
		Me.TabPage3.Controls.Add(Me.Label_Output_1to12_RelayConnection)
		Me.TabPage3.Controls.Add(Me.ListBox_Input_1to12)
		Me.TabPage3.Controls.Add(Me.TrackBar_Input_1to12)
		Me.TabPage3.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage3.Location = New System.Drawing.Point(4, 22)
		Me.TabPage3.Name = "TabPage3"
		Me.TabPage3.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage3.Size = New System.Drawing.Size(269, 443)
		Me.TabPage3.TabIndex = 0
		Me.TabPage3.Text = "TabPage3"
		Me.TabPage3.UseVisualStyleBackColor = True
		'
		'TextBox_Input_1to12_Slot
		'
		Me.TextBox_Input_1to12_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_Input_1to12_Slot.Location = New System.Drawing.Point(87, 78)
		Me.TextBox_Input_1to12_Slot.Name = "TextBox_Input_1to12_Slot"
		Me.TextBox_Input_1to12_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_Input_1to12_Slot.TabIndex = 65
		Me.TextBox_Input_1to12_Slot.Text = "4"
		'
		'Label_Input_1to12_Name
		'
		Me.Label_Input_1to12_Name.AutoSize = True
		Me.Label_Input_1to12_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Input_1to12_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Input_1to12_Name.Location = New System.Drawing.Point(28, 73)
		Me.Label_Input_1to12_Name.Name = "Label_Input_1to12_Name"
		Me.Label_Input_1to12_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_Input_1to12_Name.TabIndex = 64
		Me.Label_Input_1to12_Name.Text = "1"
		Me.Label_Input_1to12_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'CheckBox_493
		'
		Me.CheckBox_493.AutoSize = True
		Me.CheckBox_493.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_493.Location = New System.Drawing.Point(154, 139)
		Me.CheckBox_493.Name = "CheckBox_493"
		Me.CheckBox_493.Size = New System.Drawing.Size(44, 17)
		Me.CheckBox_493.TabIndex = 67
		Me.CheckBox_493.Text = "493"
		Me.CheckBox_493.UseVisualStyleBackColor = True
		'
		'CheckBox_491
		'
		Me.CheckBox_491.AutoSize = True
		Me.CheckBox_491.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_491.Location = New System.Drawing.Point(154, 119)
		Me.CheckBox_491.Name = "CheckBox_491"
		Me.CheckBox_491.Size = New System.Drawing.Size(44, 17)
		Me.CheckBox_491.TabIndex = 66
		Me.CheckBox_491.Text = "491"
		Me.CheckBox_491.UseVisualStyleBackColor = True
		'
		'Label_Output_1to12_RelayConnection
		'
		Me.Label_Output_1to12_RelayConnection.AutoSize = True
		Me.Label_Output_1to12_RelayConnection.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Output_1to12_RelayConnection.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Output_1to12_RelayConnection.Location = New System.Drawing.Point(34, 16)
		Me.Label_Output_1to12_RelayConnection.Name = "Label_Output_1to12_RelayConnection"
		Me.Label_Output_1to12_RelayConnection.Size = New System.Drawing.Size(108, 42)
		Me.Label_Output_1to12_RelayConnection.TabIndex = 63
		Me.Label_Output_1to12_RelayConnection.Text = "Bank"
		Me.Label_Output_1to12_RelayConnection.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'ListBox_Input_1to12
		'
		Me.ListBox_Input_1to12.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_Input_1to12.FormattingEnabled = True
		Me.ListBox_Input_1to12.Items.AddRange(New Object() {"IN,1,L,1,1", "IN,2,R,3,1", "IN,3,L,1,2", "IN,4,R,3,2", "IN,5,L,1,3", "IN,6,R,3,3", "IN,7,L,1,4", "IN,8,R,3,4", "IN,9,L,1,5", "IN,10,R,3,5", "IN,11,L,1,6", "IN,12,R,3,6"})
		Me.ListBox_Input_1to12.Location = New System.Drawing.Point(60, 109)
		Me.ListBox_Input_1to12.Name = "ListBox_Input_1to12"
		Me.ListBox_Input_1to12.Size = New System.Drawing.Size(88, 160)
		Me.ListBox_Input_1to12.TabIndex = 62
		'
		'TrackBar_Input_1to12
		'
		Me.TrackBar_Input_1to12.BackColor = System.Drawing.Color.FromArgb(CType(CType(128, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(255, Byte), Integer))
		Me.TrackBar_Input_1to12.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Input_1to12.LargeChange = 1
		Me.TrackBar_Input_1to12.Location = New System.Drawing.Point(31, 103)
		Me.TrackBar_Input_1to12.Maximum = 11
		Me.TrackBar_Input_1to12.Name = "TrackBar_Input_1to12"
		Me.TrackBar_Input_1to12.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_Input_1to12.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_Input_1to12.Size = New System.Drawing.Size(45, 171)
		Me.TrackBar_Input_1to12.TabIndex = 61
		Me.TrackBar_Input_1to12.Value = 1
		'
		'TabPage4
		'
		Me.TabPage4.Controls.Add(Me.TextBox_Input_13to24_Slot)
		Me.TabPage4.Controls.Add(Me.Label_Input_13to24_Name)
		Me.TabPage4.Controls.Add(Me.CheckBox_593)
		Me.TabPage4.Controls.Add(Me.CheckBox_591)
		Me.TabPage4.Controls.Add(Me.ListBox_Input_13to24)
		Me.TabPage4.Controls.Add(Me.TrackBar_Input_13to24)
		Me.TabPage4.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage4.Location = New System.Drawing.Point(4, 22)
		Me.TabPage4.Name = "TabPage4"
		Me.TabPage4.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage4.Size = New System.Drawing.Size(269, 443)
		Me.TabPage4.TabIndex = 1
		Me.TabPage4.Text = "TabPage4"
		Me.TabPage4.UseVisualStyleBackColor = True
		'
		'TextBox_Input_13to24_Slot
		'
		Me.TextBox_Input_13to24_Slot.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox_Input_13to24_Slot.Location = New System.Drawing.Point(132, 62)
		Me.TextBox_Input_13to24_Slot.Name = "TextBox_Input_13to24_Slot"
		Me.TextBox_Input_13to24_Slot.Size = New System.Drawing.Size(61, 20)
		Me.TextBox_Input_13to24_Slot.TabIndex = 64
		Me.TextBox_Input_13to24_Slot.Text = "5"
		'
		'Label_Input_13to24_Name
		'
		Me.Label_Input_13to24_Name.AutoSize = True
		Me.Label_Input_13to24_Name.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_Input_13to24_Name.Font = New System.Drawing.Font("Microsoft Sans Serif", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_Input_13to24_Name.Location = New System.Drawing.Point(60, 55)
		Me.Label_Input_13to24_Name.Name = "Label_Input_13to24_Name"
		Me.Label_Input_13to24_Name.Size = New System.Drawing.Size(19, 20)
		Me.Label_Input_13to24_Name.TabIndex = 65
		Me.Label_Input_13to24_Name.Text = "1"
		Me.Label_Input_13to24_Name.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'CheckBox_593
		'
		Me.CheckBox_593.AutoSize = True
		Me.CheckBox_593.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_593.Location = New System.Drawing.Point(170, 125)
		Me.CheckBox_593.Name = "CheckBox_593"
		Me.CheckBox_593.Size = New System.Drawing.Size(44, 17)
		Me.CheckBox_593.TabIndex = 67
		Me.CheckBox_593.Text = "593"
		Me.CheckBox_593.UseVisualStyleBackColor = True
		'
		'CheckBox_591
		'
		Me.CheckBox_591.AutoSize = True
		Me.CheckBox_591.Cursor = System.Windows.Forms.Cursors.Default
		Me.CheckBox_591.Location = New System.Drawing.Point(170, 105)
		Me.CheckBox_591.Name = "CheckBox_591"
		Me.CheckBox_591.Size = New System.Drawing.Size(44, 17)
		Me.CheckBox_591.TabIndex = 66
		Me.CheckBox_591.Text = "591"
		Me.CheckBox_591.UseVisualStyleBackColor = True
		'
		'ListBox_Input_13to24
		'
		Me.ListBox_Input_13to24.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_Input_13to24.FormattingEnabled = True
		Me.ListBox_Input_13to24.Items.AddRange(New Object() {"IN,13,L,1,1", "IN,14,R,3,1", "IN,15,L,1,2", "IN,16,R,3,2", "IN,17,L,1,3", "IN,18,R,3,3", "IN,19,L,1,4", "IN,20,R,3,4", "IN,21,L,1,5", "IN,22,R,3,5", "IN,23,L,1,6", "IN,24,R,3,6"})
		Me.ListBox_Input_13to24.Location = New System.Drawing.Point(84, 96)
		Me.ListBox_Input_13to24.Name = "ListBox_Input_13to24"
		Me.ListBox_Input_13to24.Size = New System.Drawing.Size(80, 160)
		Me.ListBox_Input_13to24.TabIndex = 63
		'
		'TrackBar_Input_13to24
		'
		Me.TrackBar_Input_13to24.BackColor = System.Drawing.Color.FromArgb(CType(CType(128, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(255, Byte), Integer))
		Me.TrackBar_Input_13to24.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_Input_13to24.LargeChange = 1
		Me.TrackBar_Input_13to24.Location = New System.Drawing.Point(55, 90)
		Me.TrackBar_Input_13to24.Maximum = 11
		Me.TrackBar_Input_13to24.Name = "TrackBar_Input_13to24"
		Me.TrackBar_Input_13to24.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_Input_13to24.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_Input_13to24.Size = New System.Drawing.Size(45, 171)
		Me.TrackBar_Input_13to24.TabIndex = 62
		Me.TrackBar_Input_13to24.Value = 1
		'
		'TabPage5
		'
		Me.TabPage5.Controls.Add(Me.Label_CardEDAC_number_B)
		Me.TabPage5.Controls.Add(Me.ListBox_CardEDAC_B)
		Me.TabPage5.Controls.Add(Me.TrackBar_CardEDAC_B)
		Me.TabPage5.Controls.Add(Me.TextBox4)
		Me.TabPage5.Cursor = System.Windows.Forms.Cursors.Default
		Me.TabPage5.Location = New System.Drawing.Point(4, 22)
		Me.TabPage5.Name = "TabPage5"
		Me.TabPage5.Padding = New System.Windows.Forms.Padding(3)
		Me.TabPage5.Size = New System.Drawing.Size(269, 443)
		Me.TabPage5.TabIndex = 2
		Me.TabPage5.Text = "TabPage5"
		Me.TabPage5.UseVisualStyleBackColor = True
		'
		'Label_CardEDAC_number_B
		'
		Me.Label_CardEDAC_number_B.AutoSize = True
		Me.Label_CardEDAC_number_B.Cursor = System.Windows.Forms.Cursors.Default
		Me.Label_CardEDAC_number_B.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_CardEDAC_number_B.Location = New System.Drawing.Point(92, 384)
		Me.Label_CardEDAC_number_B.Name = "Label_CardEDAC_number_B"
		Me.Label_CardEDAC_number_B.Size = New System.Drawing.Size(40, 42)
		Me.Label_CardEDAC_number_B.TabIndex = 69
		Me.Label_CardEDAC_number_B.Text = "1"
		Me.Label_CardEDAC_number_B.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
		'
		'ListBox_CardEDAC_B
		'
		Me.ListBox_CardEDAC_B.Cursor = System.Windows.Forms.Cursors.Default
		Me.ListBox_CardEDAC_B.FormattingEnabled = True
		Me.ListBox_CardEDAC_B.Items.AddRange(New Object() {"A-1", "B-2", "C-3", "D-4", "E-5", "F-6", "H-7", "J-8", "K-9", "L-10", "M-11", "N-12", "P-13", "R-14", "S-15", "T-16", "U-17", "V-18", "W-19", "X-20", "Y-21", "Z-22", "NC", "NC"})
		Me.ListBox_CardEDAC_B.Location = New System.Drawing.Point(116, 52)
		Me.ListBox_CardEDAC_B.Name = "ListBox_CardEDAC_B"
		Me.ListBox_CardEDAC_B.Size = New System.Drawing.Size(41, 316)
		Me.ListBox_CardEDAC_B.TabIndex = 68
		'
		'TrackBar_CardEDAC_B
		'
		Me.TrackBar_CardEDAC_B.BackColor = System.Drawing.Color.FromArgb(CType(CType(255, Byte), Integer), CType(CType(128, Byte), Integer), CType(CType(0, Byte), Integer))
		Me.TrackBar_CardEDAC_B.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar_CardEDAC_B.LargeChange = 1
		Me.TrackBar_CardEDAC_B.Location = New System.Drawing.Point(87, 46)
		Me.TrackBar_CardEDAC_B.Maximum = 23
		Me.TrackBar_CardEDAC_B.Name = "TrackBar_CardEDAC_B"
		Me.TrackBar_CardEDAC_B.Orientation = System.Windows.Forms.Orientation.Vertical
		Me.TrackBar_CardEDAC_B.RightToLeft = System.Windows.Forms.RightToLeft.Yes
		Me.TrackBar_CardEDAC_B.Size = New System.Drawing.Size(45, 328)
		Me.TrackBar_CardEDAC_B.TabIndex = 67
		Me.TrackBar_CardEDAC_B.Value = 1
		'
		'TextBox4
		'
		Me.TextBox4.Cursor = System.Windows.Forms.Cursors.Default
		Me.TextBox4.Location = New System.Drawing.Point(49, 7)
		Me.TextBox4.Name = "TextBox4"
		Me.TextBox4.Size = New System.Drawing.Size(61, 20)
		Me.TextBox4.TabIndex = 66
		Me.TextBox4.Text = "6"
		'
		'TrackBar1
		'
		Me.TrackBar1.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar1.Location = New System.Drawing.Point(282, 699)
		Me.TrackBar1.Name = "TrackBar1"
		Me.TrackBar1.Size = New System.Drawing.Size(104, 45)
		Me.TrackBar1.TabIndex = 226
		'
		'TrackBar2
		'
		Me.TrackBar2.Cursor = System.Windows.Forms.Cursors.Default
		Me.TrackBar2.Location = New System.Drawing.Point(463, 699)
		Me.TrackBar2.Name = "TrackBar2"
		Me.TrackBar2.Size = New System.Drawing.Size(104, 45)
		Me.TrackBar2.TabIndex = 227
		'
		'Router
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.Controls.Add(Me.TrackBar2)
		Me.Controls.Add(Me.TrackBar1)
		Me.Controls.Add(Me.TabControl4)
		Me.Controls.Add(Me.TabControl3)
		Me.Controls.Add(Me.TabControl1)
		Me.Controls.Add(Me.TabControl2)
		Me.Name = "Router"
		Me.Size = New System.Drawing.Size(698, 1000)
		EDAC_2.ResumeLayout(False)
		Me.GroupBox6.ResumeLayout(False)
		Me.GroupBox6.PerformLayout()
		CType(Me.TrackBar_Output_13to24, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabControl1.ResumeLayout(False)
		Me.EDAC_1.ResumeLayout(False)
		Me.GroupBox1.ResumeLayout(False)
		Me.GroupBox1.PerformLayout()
		CType(Me.TrackBar_Output_1to12, System.ComponentModel.ISupportInitialize).EndInit()
		Me.EDAC_3.ResumeLayout(False)
		Me.GroupBox4.ResumeLayout(False)
		Me.GroupBox4.PerformLayout()
		CType(Me.TrackBar_CardEDAC_A, System.ComponentModel.ISupportInitialize).EndInit()
		Me.Busses.ResumeLayout(False)
		Me.GroupBox3.ResumeLayout(False)
		Me.GroupBox3.PerformLayout()
		CType(Me.TrackBar_Bus, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabControl2.ResumeLayout(False)
		Me.Tone_and_Music.ResumeLayout(False)
		Me.Tone_and_Music.PerformLayout()
		CType(Me.PictureBox_Output, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabPage6.ResumeLayout(False)
		Me.TabPage6.PerformLayout()
		CType(Me.TrackBar_Output_SELECT, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.OUTPUT_Select, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabControl3.ResumeLayout(False)
		Me.TabPage1.ResumeLayout(False)
		Me.TabPage1.PerformLayout()
		CType(Me.PictureBox3, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.PictureBox4, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabPage2.ResumeLayout(False)
		Me.TabPage2.PerformLayout()
		CType(Me.TrackBar_input_SELECT, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabControl4.ResumeLayout(False)
		Me.TabPage3.ResumeLayout(False)
		Me.TabPage3.PerformLayout()
		CType(Me.TrackBar_Input_1to12, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabPage4.ResumeLayout(False)
		Me.TabPage4.PerformLayout()
		CType(Me.TrackBar_Input_13to24, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TabPage5.ResumeLayout(False)
		Me.TabPage5.PerformLayout()
		CType(Me.TrackBar_CardEDAC_B, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar1, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar2, System.ComponentModel.ISupportInitialize).EndInit()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents TabControl1 As TabControl
	Friend WithEvents EDAC_3 As TabPage
	Friend WithEvents GroupBox4 As GroupBox
	Friend WithEvents TextBox_CardEDAC_Slot As TextBox
	Friend WithEvents Label_CardEDAC_RelayConnection As Label
	Friend WithEvents Label_CardEDAC_number_A As Label
	Friend WithEvents CheckBox_EDAC_TIE As CheckBox
	Friend WithEvents ListBox_CardEDAC_A As ListBox
	Friend WithEvents TrackBar_CardEDAC_A As TrackBar
	Friend WithEvents Label_CardEDAC_Name As Label
	Friend WithEvents EDAC_1 As TabPage
	Friend WithEvents GroupBox1 As GroupBox
	Friend WithEvents Label_Output_1to12_Name As Label
	Friend WithEvents Label_Input_1to12_RelayConnection As Label
	Friend WithEvents TextBox_Output_1to12_Slot As TextBox
	Friend WithEvents ListBox_Output_1to12 As ListBox
	Friend WithEvents TrackBar_Output_1to12 As TrackBar
	Friend WithEvents Busses As TabPage
	Friend WithEvents GroupBox3 As GroupBox
	Friend WithEvents TextBox_Bus_Slot As TextBox
	Friend WithEvents Label_Bus_RelayConnection As Label
	Friend WithEvents Label_Bus_Number As Label
	Friend WithEvents ListBox_Bus As ListBox
	Friend WithEvents TrackBar_Bus As TrackBar
	Friend WithEvents Label_Bus_Name As Label
	Friend WithEvents TabControl2 As TabControl
	Friend WithEvents Tone_and_Music As TabPage
	Friend WithEvents CheckBox_Tone_Left As CheckBox
	Friend WithEvents CheckBox_Tone_Right As CheckBox
	Friend WithEvents check_input_output_link As CheckBox
	Friend WithEvents CheckBox_Music_Left As CheckBox
	Friend WithEvents CheckBox_Music_Right As CheckBox
	Friend WithEvents PictureBox_Output As PictureBox
	Friend WithEvents Multiplexor_Inputs As TabPage
	Friend WithEvents OUTPUT_Select As TrackBar
	Friend WithEvents TextBox1 As TextBox
	Friend WithEvents TextBox13 As TextBox
	Friend WithEvents GroupBox6 As GroupBox
	Friend WithEvents Label_Output_13to24_Name As Label
	Friend WithEvents Label_Input_13to24_RelayConnection As Label
	Friend WithEvents Label_Output_13to24_RelayConnection As Label
	Friend WithEvents TextBox_Output_13to24_Slot As TextBox
	Friend WithEvents ListBox_Output_13to24 As ListBox
	Friend WithEvents TrackBar_Output_13to24 As TrackBar
	Friend WithEvents TabControl3 As TabControl
	Friend WithEvents TabPage1 As TabPage
	Friend WithEvents PictureBox3 As PictureBox
	Friend WithEvents PictureBox4 As PictureBox
	Friend WithEvents CheckBox_Dest_Right As CheckBox
	Friend WithEvents CheckBox_Monitor_Left As CheckBox
	Friend WithEvents CheckBox_Dest_Left As CheckBox
	Friend WithEvents CheckBox_Monitor_Right As CheckBox
	Friend WithEvents TabPage2 As TabPage
	Friend WithEvents TextBox2 As TextBox
	Friend WithEvents TextBox3 As TextBox
	Friend WithEvents TrackBar_input_SELECT As TrackBar
	Friend WithEvents TabControl4 As TabControl
	Friend WithEvents TabPage3 As TabPage
	Friend WithEvents TextBox_Input_1to12_Slot As TextBox
	Friend WithEvents Label_Input_1to12_Name As Label
	Friend WithEvents CheckBox_493 As CheckBox
	Friend WithEvents CheckBox_491 As CheckBox
	Friend WithEvents Label_Output_1to12_RelayConnection As Label
	Friend WithEvents ListBox_Input_1to12 As ListBox
	Friend WithEvents TrackBar_Input_1to12 As TrackBar
	Friend WithEvents TabPage4 As TabPage
	Friend WithEvents TextBox_Input_13to24_Slot As TextBox
	Friend WithEvents Label_Input_13to24_Name As Label
	Friend WithEvents CheckBox_593 As CheckBox
	Friend WithEvents CheckBox_591 As CheckBox
	Friend WithEvents ListBox_Input_13to24 As ListBox
	Friend WithEvents TrackBar_Input_13to24 As TrackBar
	Friend WithEvents TabPage5 As TabPage
	Friend WithEvents Label_CardEDAC_number_B As Label
	Friend WithEvents ListBox_CardEDAC_B As ListBox
	Friend WithEvents TrackBar_CardEDAC_B As TrackBar
	Friend WithEvents TextBox4 As TextBox
	Friend WithEvents TrackBar1 As TrackBar
	Friend WithEvents TrackBar2 As TrackBar
	Friend WithEvents TabPage6 As TabPage
	Friend WithEvents TextBox5 As TextBox
	Friend WithEvents TextBox6 As TextBox
	Friend WithEvents TrackBar_Output_SELECT As TrackBar
End Class
