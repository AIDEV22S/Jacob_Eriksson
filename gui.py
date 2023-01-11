import operator
import PySimpleGUI as sg
from backend import Members
from backend import retrieve_members
from backend import session
from backend import create_engine

sg.theme('DarkGreen5')
create_engine()

# En funktion som sorterar table-värden baserat på vilken kolumn man önskar sortera i.
def sort_table(data, col_num_clicked):
    try:
        table_data = sorted(data, key=operator.itemgetter(col_num_clicked))
        return table_data
    except Exception as e:
        sg.popup_error(f'Exception: {e}')

# Andra window, för när vi ska fylla i värden för nya members i vår databas
def create_add_member_window():
    layout = [
        [sg.T('First Name:'), sg.P(), sg.I(key='-FIRST_NAME-', do_not_clear=False)],
        [sg.T('Last Name:'),sg.P(), sg.I(key='-LAST_NAME-', do_not_clear=False)],
        [sg.T('Street Address:'),sg.P(), sg.I(key='-STREET_ADDRESS-', do_not_clear=False)],
        [sg.T('Post Address:'),sg.P(), sg.I(key='-POST_ADDRESS-', do_not_clear=False)],
        [sg.T('Post Number:'),sg.P(), sg.I(key='-POST_NUMBER-', do_not_clear=False)],
        [sg.T('Paid Fee:         '), sg.R('Yes', 'RADIO', key='-PAID_YES-'), sg.R('No', 'RADIO', key='-PAID_NO-')],
        [sg.B('Add Member', key='-ADD_MEMBER-', bind_return_key=True), sg.B('Exit', button_color='Red')]]
    return sg.Window('Add Members', layout, finalize=True, enable_close_attempted_event=True)

# primära window, som vi primärt integrera med.
def create_primary_window():
    headings = ['Member ID', 'First Name', 'Last Name', 'Street Address', 'Post Address', 'Post Number', 'Paid Fee']
    layout = [
        [sg.B('Add Members'), sg.B('Delete Member', key='-DELETE_MEMBER-'), sg.B('Search Members', key='-SEARCH-'),
        sg.I(key='-S_INPUT-'), sg.B('Refresh Table', key='-REFRESH_TABLE-'), sg.B('Exit', button_color='Red')],
        [sg.Table(
            values=retrieve_members(), key='-TABLE-',
            headings=headings, auto_size_columns=True, display_row_numbers=False, justification='right', num_rows=20,
            enable_events=True, enable_click_events=True, expand_x=True, expand_y=True,
            alternating_row_color='#3D3B3B')]]
    return sg.Window('Member Manager', layout, finalize=True)

# main sköter alla funktioner för hur vår gui används och adderar/subtraherar/söker medlemmar
# Det är denna vi kommer kalla på i main när vi önskar köra programmet
def main():
    main_window, add_member_window = create_primary_window(), None
    def update_table(changed_values):
        return main_window['-TABLE-'].update(values=changed_values)

    def create_member():
        try:
            user = Members(
                First_Name=values['-FIRST_NAME-'], Last_Name=values['-LAST_NAME-'],
                Street_Address=values['-STREET_ADDRESS-'], Post_Address=values['-POST_ADDRESS-'],
                Post_Number=values['-POST_NUMBER-'],
                Paid_Fee=values['-PAID_YES-'] == True or ['-PAID_NO-'] == False)
            session.add(user)
            session.expire_on_commit = False
            session.commit()
            sg.popup_ok(f'Added member: {user.First_Name} {user.Last_Name}', auto_close=True, auto_close_duration=0.5)
            update_table(retrieve_members())
        except Exception as ex:
            sg.popup_error(f'Error, exception: {ex}')

    def delete_member():
        try:
            if sg.popup_yes_no('Are you sure you want to delete this member?') == 'Yes':
                selected_row_index = values['-TABLE-']
                selected_member = (retrieve_members()[selected_row_index[0]])
                selected_id = selected_member[0]
                members_to_delete = session.get(Members, selected_id)
                session.delete(members_to_delete)
                session.expire_on_commit = False
                session.commit()
                update_table(retrieve_members())
                sg.popup_ok(f'Deleted member: {selected_member[1]} {selected_member[2]}',
                            auto_close=True, auto_close_duration=1)
            else:
                return
        except Exception as exc:
            sg.popup_error(f'Error, you probably did not select a row to delete. exception: {exc}')

    main_window.bind('<Return>', '_ENTER'), main_window.bind('<Alt_L><a>', '_ADD'),\
    main_window.bind('<Alt_L><d>','_DEL'), main_window.bind('<Delete>', '_DELETE'),\
    main_window.bind('<Escape>', '_ESC'), main_window.bind('<Alt_L><s>','_SEARCH'),\

    # Main-event loop, det är här vi gör alla våra saker relaterade till gui
    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED or event == 'Exit' or event == '_D_ENTER' or event == '_ESC':
            if window == add_member_window:
                add_member_window.close()
                add_member_window = None
            elif window == main_window:
                if sg.popup_yes_no('Are you sure you want to exit?') == 'Yes':
                    break
        elif event == 'Add Members' or event == '_ADD' and not add_member_window:
            add_member_window = create_add_member_window()
            add_member_window.bind('<Escape>', '_ESC')
        elif event == '-ADD_MEMBER-' and window == add_member_window:
            create_member()
        elif event == '-DELETE_MEMBER-' or event == '_DEL' or event == '_DELETE':
            delete_member()
        elif event == '-SEARCH-' or event == '_SEARCH':
            try:
                if values['-S_INPUT-'] != '':
                    new_values = [x for x in retrieve_members() if values['-S_INPUT-'] in x]
                    update_table(new_values)
            except Exception as e:
                sg.popup_error(f'Exception: {e}')
        elif event == '_ENTER' or event == 'Refresh Table':
            update_table(retrieve_members())
        elif isinstance(event, tuple):
            if event[0] == '-TABLE-':
                if event[2][0] == -1 and event[2][1] != -1:
                    col_num_clicked = event[2][1]
                    sorted_table_data = sort_table(retrieve_members(), col_num_clicked)
                    update_table(sorted_table_data)
    window.close()