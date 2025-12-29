Public Class DCLoadForm


    Public DCloadGPIBManager As Ivi.Visa.Interop.ResourceManager

    Public Structure DCloadDevice
        Dim Connected As Boolean

        Dim GPIBAddress As String

        'Status from unit
        Dim StatusEngaged As Boolean ' ON or OFF
        Dim StatusMode As String ' the status of the "mode" of the unit

        'Linking with power supplies
        Dim Link As Integer ' the channel it is linked to

        'Module Parameters
        Dim ModuleMaxVoltage As Double ' Maximum voltage module is capable of
        Dim ModuleMaxCurrent As Double ' maximum current from PSU

        'Controls
        Dim SendVoltage As Double ' The Voltage sent to the PSU
        Dim SendCurrentLimit As Double ' the current limit of 
        Dim SendResistance As Double ' the current limit of 


        'Recieve 
        Dim ReadVoltage As Double ' the voltage read by the PSU
        Dim ReadCurrent As Double ' the Current of the PSU
        Dim ReadPower As Double ' the Current of the PSU
        Dim ReadResistance As Double ' the Current of the PSU


        Dim CalcPower As Double ' Calculated Power

        Dim SCIP As Ivi.Visa.Interop.FormattedIO488
    End Structure




    Public DCload(1) As DCloadDevice


    Dim DCLoadDeviceID As Integer = 1






    Private Sub DCLoadForm_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        UserInterfaceShell.ProgramableLoadToolStripMenuItem.Checked = True



		Try
			DCload(1).GPIBAddress = 21
			addressDCLoad(1) '

			AppliedResistanceExact.Text = 1000

		Catch ex As Exception

		End Try


	End Sub


	Public Sub addressDCLoad(chanel As Integer)


		CommandList("addressDCLoad()")



		Dim GPIB_IP As String = "192.168.0.106"
		Dim GPIB_BUSS As Integer = "7"


		Dim TCPIConfiguration As String = "TCPIP0::" & GPIB_IP & "::" & GPIB_BUSS & "," & DCload(DCLoadDeviceID).GPIBAddress & "::INSTR"

		'Address Modules Individually 
		Try

			DCloadGPIBManager = New Ivi.Visa.Interop.ResourceManager
			DCload(DCLoadDeviceID).SCIP = New Ivi.Visa.Interop.FormattedIO488
			DCload(DCLoadDeviceID).SCIP.IO = DCloadGPIBManager.Open((TCPIConfiguration))    ' 10 is the instr. address 

			'CLEAR STATUS

			DCload(DCLoadDeviceID).SCIP.WriteString("*CLS")
			DCload(DCLoadDeviceID).Connected = True
		Catch ex As Exception

			DCload(DCLoadDeviceID).Connected = False
		End Try

	End Sub



	Private Sub DCLoadForm_Close(sender As Object, e As EventArgs) Handles MyBase.Closed
        UserInterfaceShell.ProgramableLoadToolStripMenuItem.Checked = False
        DCload(DCLoadDeviceID).Connected = False
    End Sub

    Private Sub LoadApplied_Click(sender As Object, e As EventArgs) Handles BusttonDCLoadApplied.Click
        DCResistiveload()
        ToggleStatus()
        DCloadMeasureAll(DCLoadDeviceID)
    End Sub

    Public Sub DCResistiveload()



		Try
			'Set mode
			DCload(DCLoadDeviceID).SCIP.WriteString("mode:res")

		Catch ex As Exception

		End Try

		'confirm mode
		CheckDCloadConfigurationStatus()

    End Sub

    Public Sub ToggleStatus()

        If DCload(DCLoadDeviceID).StatusEngaged = False Then

            'turn it on
            Try

                DCload(DCLoadDeviceID).SCIP.WriteString("inp:stat on")

                'change status indication only if it confirmed externally
                CheckDCloadConfigurationStatus()
                If DCload(DCLoadDeviceID).StatusEngaged = True Then
                    BusttonDCLoadApplied.BackColor = Color.DarkOrange
                    BusttonDCLoadApplied.Text = "--/\/\/\/\---LOADED"
                End If

            Catch ex As Exception

            End Try




        ElseIf DCload(DCLoadDeviceID).StatusEngaged = True Then
            'turn it off
            Try
                DCload(DCLoadDeviceID).SCIP.WriteString("inp:stat off")

                'change status indication only if it confirmed externally
                CheckDCloadConfigurationStatus()
                If DCload(DCLoadDeviceID).StatusEngaged = False Then
                    BusttonDCLoadApplied.BackColor = Color.RoyalBlue
                    BusttonDCLoadApplied.Text = "Apply ___/  __ Load"

                End If
            Catch ex As Exception
            End Try

        End If


    End Sub

    Public Sub CheckDCloadConfigurationStatus()
		Try
			DCload(DCLoadDeviceID).SCIP.WriteString("inp:stat?")
			DCload(DCLoadDeviceID).StatusEngaged = DCload(DCLoadDeviceID).SCIP.ReadString
			BarGraphVoltage.Value = DCload(DCLoadDeviceID).ReadVoltage
			DCload(DCLoadDeviceID).SCIP.WriteString("mode?")
			DCload(DCLoadDeviceID).StatusMode = DCload(DCLoadDeviceID).SCIP.ReadString
		Catch ex As Exception

		End Try




	End Sub


    Public Sub DCloadMeasureAll(DCLoadDeviceID)
        DCloadMeasureVoltage(DCLoadDeviceID)
        DCloadMeasureCurrent(DCLoadDeviceID)
        DCloadMeasurePower(DCLoadDeviceID)
    End Sub

    Private Sub DCloadMeasureVoltage(DCLoadDeviceID)

        Try
            DCload(DCLoadDeviceID).SCIP.WriteString("measure:volt?")
            DCload(DCLoadDeviceID).ReadVoltage = DCload(DCLoadDeviceID).SCIP.ReadNumber
            BarGraphVoltage.Value = DCload(DCLoadDeviceID).ReadVoltage
            ValueNumberVoltage.Text = DCload(DCLoadDeviceID).ReadVoltage
        Catch ex As Exception
            ValueNumberVoltage.Text = "ERROR"
            BarGraphVoltage.Value = 0
        End Try

    End Sub

    Private Sub DCloadMeasureCurrent(DCLoadDeviceID)
        Try
            DCload(DCLoadDeviceID).SCIP.WriteString("measure:curr?")
            DCload(DCLoadDeviceID).ReadCurrent = DCload(DCLoadDeviceID).SCIP.ReadNumber
            BarGraphCurrent.Value = DCload(DCLoadDeviceID).ReadCurrent
            ValueNumberCurrent.Text = DCload(DCLoadDeviceID).ReadCurrent
        Catch ex As Exception
            ValueNumberCurrent.Text = "ERROR"
            BarGraphCurrent.Value = 0
        End Try
    End Sub

    Private Sub DCloadMeasurePower(DCLoadDeviceID)

        Try
            DCload(DCLoadDeviceID).SCIP.WriteString("measure:pow?")
            DCload(DCLoadDeviceID).ReadPower = DCload(DCLoadDeviceID).SCIP.ReadNumber
            BarGraphPower.Value = DCload(DCLoadDeviceID).ReadPower
            ValueNumberPower.Text = DCload(DCLoadDeviceID).ReadPower
        Catch ex As Exception
            ValueNumberPower.Text = "ERROR"
            BarGraphPower.Value = 0
        End Try

    End Sub




    Public Sub DCLoadChangeResistance(DCLoadDeviceID, Value)

        Try
            DCload(DCLoadDeviceID).SCIP.WriteString("res:lev " & Value)


            DCload(DCLoadDeviceID).SCIP.WriteString("res:lev?")
            DCload(DCLoadDeviceID).ReadResistance = DCload(DCLoadDeviceID).SCIP.ReadNumber



            BarGraphResistance.Value = DCload(DCLoadDeviceID).ReadResistance
            ValueNumberResistance.Text = DCload(DCLoadDeviceID).ReadResistance
            DCloadMeasureAll(DCLoadDeviceID)

        Catch ex As Exception
            ValueNumberResistance.Text = "ERROR"
            BarGraphResistance.Value = 0
        End Try
    End Sub


	'USER INTERFACE



	Private Sub AppliedResistanceExact_TextChanged(sender As Object, e As EventArgs) Handles AppliedResistanceExact.Leave

		Dim TextTest As Double = CDbl(AppliedResistanceExact.Text)
		If TextTest > 0 And TextTest <= 1000 Then
			DCLoadChangeResistance(DCLoadDeviceID, TextTest)
			AppliedResistance.Value = CDbl(AppliedResistanceExact.Text)
		End If

	End Sub

	Private Sub AppliedResistance_Scroll(sender As Object, e As EventArgs) Handles AppliedResistance.Scroll
        AppliedResistanceExact.Text = AppliedResistance.Value
    End Sub


    Private Sub Button1_Click_1(sender As Object, e As EventArgs) Handles Button1.Click
        DCloadMeasureAll(DCLoadDeviceID)
    End Sub

	Private Sub InitializeComponent()
		Me.SuspendLayout()
		'
		'DCLoadForm
		'
		Me.ClientSize = New System.Drawing.Size(637, 505)
		Me.Name = "DCLoadForm"
		Me.ResumeLayout(False)

	End Sub


End Class