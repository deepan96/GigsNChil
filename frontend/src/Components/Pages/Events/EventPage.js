import {
  Card,
  CardActions,
  CardContent,
  CardMedia,
  IconButton,
} from "@material-ui/core";
import FavoriteIcon from "@mui/icons-material/Favorite";
import ShareIcon from "@mui/icons-material/Share";
import React, { useEffect, useState } from "react";
import styles from "./EventPage.module.css";
import bgimage from "../Promote-Your-local-event.jpg";
import { useParams } from "react-router-dom";
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
import { Alert } from "@mui/material";
import { red } from "@material-ui/core/colors";
import ModalPop from "../../ModalPop/ModalPop";
import moment from "moment";

export default function EventPage(props) {
  const { id } = useParams();
  const [event, setEvent] = useState();
  const [eventData, setEventData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fav, setFav] = useState(true); // setting bookmark
  const [noftickets, setNoftickets] = useState(1);
  const [modelOpen, setModelOpen] = useState(false);

  const [errorFound, setErrorFound] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [errorSeverity, setErrorSeverity] = useState("error");
  const [successVar, setSuccessvar] = useState(false);

  const user_info = JSON.parse(localStorage.getItem("user"));

  var axios = require("axios");
  var config = {
    method: "get",
    url: "https://gigsnchill.herokuapp.com/searchevent/",
  };
  // getting events data

  useEffect(() => {
    setLoading(true);

    axios(config).then((res) => {
      console.log(res.data.data);
      setEventData(res.data.data);

      console.log(eventData);
      const eventId = res.data.data.filter(
        (e) => e.EventId === parseInt(id)
      )[0];
      console.log(eventId);
      setEvent(eventId);
      // setFav(false);
      console.log(moment(eventId.EventDate).format("MMMM Do YYYY"));
      setLoading(false);
    });
    setNoftickets(1);
    
    // setErrorFound(false);
    // setErrorMessage("");
  }, [successVar]);

  function handleFav() {
    setFav(prev=>!prev);
    console.log("like", fav);
    const user_info = JSON.parse(localStorage.getItem("user"));
    // making a bookmark
    var data = new FormData();
    data.append("UserId", user_info.email);
    data.append("EventId", id);
    data.append("BookmarkStatus", fav);
    var config = {
      method: "post",
      url: "https://gigsnchill.herokuapp.com/bookmarkevent/",
      data: data,
    };

    axios(config)
      .then((res) => {
        console.log(res.data.data);
        alert("BookMark Success!");
      })
      .catch((err) => {
        alert("Invalid BookMark Request");
        console.log(err);
      });
  }

  function invokeShare() {
    setModelOpen(!modelOpen);
    console.log(modelOpen);
  }

  async function countPlus() {
    await setNoftickets((prev) => (prev + 1 > 6 ? 6 : prev + 1));
    console.log(noftickets);
  }
  async function countMinus() {
    await setNoftickets((prev) => (prev - 1 > 0 ? prev - 1:1));
    console.log(noftickets);
  }
  
  async function handleRegistration() {
    console.log("Making registration");
    var FormData = require("form-data");
    var data = new FormData();
    data.append("UserId", user_info.email);
    data.append("NoOfSeats", noftickets);
    data.append("EventId", id);
    var config = {
      method: "post",
      url: "https://gigsnchill.herokuapp.com/bookevent/",
      data: data,
    };
    axios(config)
      .then((res) => {
        if (res.data.status === "error") {
          console.log(res);
          console.log("error");
          setErrorFound(true);
          setErrorMessage(res.data.message);
          console.log(errorMessage);
        } else {
          setErrorSeverity("success");
          setErrorFound(true);
          setErrorMessage("Successfully booked! :]");
          console.log("sucess");
          setSuccessvar((prev) => !prev);
        }
        setTimeout(() => {
          setErrorFound(false);
          setErrorMessage("");
        }, 3000);
      })
      .catch((err) => {
        alert("Invalid Booking");
      });
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={styles}>
      <div className={styles.fullpage}>
        <Card className={styles.container}>
          <div className={styles.imagediv}>
            <CardMedia
              className={styles.cardimage}
              image={event.ImageUrl}
              alt="event image"
            />
          </div>
          <div className={styles.cardcontent}>
            <CardContent>
              <div className={styles.eventtitle}>
                <h3>{event.EventName}</h3>
                <div>
                  <CardActions disableSpacing>
                    <IconButton
                      aria-label="add to favorites"
                      sx={{ color: red[500] }}
                      onClick={handleFav}
                    >
                      {fav && <FavoriteIcon sx={{ color: "red" }} />}
                      {!fav && <FavoriteIcon />}
                    </IconButton>
                    <IconButton aria-label="share">
                      <ShareIcon onClick={invokeShare} />
                      {/* {modelOpen && <ModalPop/>} */}
                    </IconButton>
                  </CardActions>
                  <ModalPop eventid = {id}  invokefunc={invokeShare} open={modelOpen} />
                </div>
                <div className={styles.eventdetails}>
                  <div className={styles.eventdate}>
                    <p>{moment(event.EventDate).format("MMMM Do YYYY")}</p>
                  </div>
                  <div className={styles.eventtime}>
                    <p>
                      Time : {event.EventStartTime} --{" "}
                      {event.EventEndTime}
                    </p>
                  </div>
                  <div className={styles.eventtype}>
                    <h5>Category : {event.EventGenre}</h5>
                    <h5>Type : {event.EventType}</h5>
                  </div>
                  <div className={styles.eventlocation}>
                    <p>Address :</p>
                    {}
                    <p>
                      {event.Address},{event.ZipCode}
                    </p>
                  </div>
                  <div className={styles.eventtime}>
                    <p>
                      Date and time : {event.EventStartTime} -- {" "}
                      {event.EventEndTime}
                    </p>
                  </div>
                </div>
                <p>{event.EventDescription}</p>
              </div>
            </CardContent>

            <div className={styles.countbutton}>
              {errorFound && (
                <Alert severity={errorSeverity} cl>
                  {errorMessage}
                </Alert>
              )}
              <div className={styles.eventseats}>
                <p>No. of Tickets left : {event.SeatsAvailable}</p>
              </div>
              <br></br>
              <div className={styles.countplus}>
                <IconButton onClick={countMinus}>
                  <RemoveIcon />
                </IconButton>

                <div style={{ margin: "1em" }}>{noftickets}</div>

                <IconButton onClick={countPlus}>
                  {/* () => setNoftickets((prev) => prev + 1) */}
                  <AddIcon />
                </IconButton>
              </div>
            </div>
            <div className={styles.eventregister}>
              <button type="button" onClick={handleRegistration}>
                Book Ticket
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
